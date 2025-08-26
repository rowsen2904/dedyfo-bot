"""Notification service for managing user notifications."""

import logging
from datetime import datetime
from typing import List, Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import DatabaseManager, Notification, NotificationStatus, NotificationType, User
from .base import BaseService

logger = logging.getLogger(__name__)


class NotificationService(BaseService[Notification]):
    """Service for managing notifications."""
    
    def __init__(self, db_manager: DatabaseManager, bot: Bot) -> None:
        """Initialize notification service."""
        super().__init__(Notification, db_manager)
        self.bot = bot
    
    async def create_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        user_id: Optional[int] = None,
        scheduled_at: Optional[datetime] = None,
        is_broadcast: bool = False,
        priority: int = 1,
    ) -> Notification:
        """Create a new notification."""
        async with self.db_manager.get_session() as session:
            notification = await self.create(
                session,
                title=title,
                message=message,
                type=notification_type,
                user_id=user_id,
                scheduled_at=scheduled_at or datetime.utcnow(),
                is_broadcast=is_broadcast,
                priority=priority,
            )
            logger.info(f"Created notification: {title}")
            return notification
    
    async def send_notification(self, notification_id: int) -> bool:
        """Send a specific notification."""
        async with self.db_manager.get_session() as session:
            notification = await self.get_by_id(session, notification_id)
            if not notification:
                logger.error(f"Notification {notification_id} not found")
                return False
            
            if notification.status != NotificationStatus.PENDING:
                logger.warning(f"Notification {notification_id} is not pending")
                return False
            
            success = False
            
            if notification.is_broadcast:
                success = await self._send_broadcast_notification(session, notification)
            elif notification.user_id:
                success = await self._send_user_notification(session, notification)
            else:
                logger.error(f"Notification {notification_id} has no target")
                return False
            
            # Update notification status
            status = NotificationStatus.SENT if success else NotificationStatus.FAILED
            await self.update(
                session,
                notification,
                status=status,
                sent_at=datetime.utcnow() if success else None
            )
            
            return success
    
    async def _send_user_notification(
        self, 
        session: AsyncSession, 
        notification: Notification
    ) -> bool:
        """Send notification to a specific user."""
        try:
            # Format message with title
            full_message = f"<b>{notification.title}</b>\n\n{notification.message}"
            
            await self.bot.send_message(
                chat_id=notification.user_id,
                text=full_message,
                parse_mode="HTML"
            )
            
            logger.info(f"Sent notification to user {notification.user_id}")
            return True
            
        except TelegramForbiddenError:
            logger.warning(f"User {notification.user_id} blocked the bot")
            await self.update(
                session,
                notification,
                error_message="User blocked the bot"
            )
            return False
            
        except TelegramBadRequest as e:
            logger.error(f"Bad request sending notification to {notification.user_id}: {e}")
            await self.update(
                session,
                notification,
                error_message=str(e)
            )
            return False
            
        except Exception as e:
            logger.error(f"Error sending notification to {notification.user_id}: {e}")
            await self.update(
                session,
                notification,
                error_message=str(e)
            )
            return False
    
    async def _send_broadcast_notification(
        self, 
        session: AsyncSession, 
        notification: Notification
    ) -> bool:
        """Send notification to all active users."""
        try:
            # Get all active users
            result = await session.execute(
                select(User.id)
                .where(User.status == "active")
            )
            user_ids = [user_id for user_id, in result.all()]
            
            if not user_ids:
                logger.warning("No active users found for broadcast")
                return False
            
            # Format message
            full_message = f"<b>{notification.title}</b>\n\n{notification.message}"
            
            sent_count = 0
            failed_count = 0
            
            # Send to each user
            for user_id in user_ids:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=full_message,
                        parse_mode="HTML"
                    )
                    sent_count += 1
                    
                except (TelegramForbiddenError, TelegramBadRequest):
                    failed_count += 1
                    continue
                    
                except Exception as e:
                    logger.error(f"Error sending broadcast to {user_id}: {e}")
                    failed_count += 1
                    continue
            
            logger.info(f"Broadcast sent to {sent_count} users, {failed_count} failed")
            
            # Update notification with stats
            await self.update(
                session,
                notification,
                message=f"{notification.message}\n\n[Sent to {sent_count} users, {failed_count} failed]"
            )
            
            return sent_count > 0
            
        except Exception as e:
            logger.error(f"Error sending broadcast notification: {e}")
            await self.update(
                session,
                notification,
                error_message=str(e)
            )
            return False
    
    async def send_pending_notifications(self) -> int:
        """Send all pending notifications that are due."""
        async with self.db_manager.get_session() as session:
            now = datetime.utcnow()
            
            result = await session.execute(
                select(Notification)
                .where(
                    and_(
                        Notification.status == NotificationStatus.PENDING,
                        Notification.scheduled_at <= now
                    )
                )
                .order_by(Notification.priority.desc(), Notification.created_at)
            )
            
            notifications = result.scalars().all()
            sent_count = 0
            
            for notification in notifications:
                if await self.send_notification(notification.id):
                    sent_count += 1
            
            logger.info(f"Sent {sent_count} pending notifications")
            return sent_count
    
    async def get_user_notifications(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a specific user."""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
    
    async def cancel_notification(self, notification_id: int) -> bool:
        """Cancel a pending notification."""
        async with self.db_manager.get_session() as session:
            notification = await self.get_by_id(session, notification_id)
            
            if not notification:
                return False
            
            if notification.status != NotificationStatus.PENDING:
                return False
            
            await self.update(
                session,
                notification,
                status=NotificationStatus.CANCELLED
            )
            
            logger.info(f"Cancelled notification {notification_id}")
            return True
    
    async def get_notification_stats(self) -> dict:
        """Get notification statistics."""
        async with self.db_manager.get_session() as session:
            # Total notifications
            total_result = await session.execute(
                select(func.count(Notification.id))
            )
            total = total_result.scalar()
            
            # By status
            status_result = await session.execute(
                select(Notification.status, func.count(Notification.id))
                .group_by(Notification.status)
            )
            by_status = {status: count for status, count in status_result.all()}
            
            # By type
            type_result = await session.execute(
                select(Notification.type, func.count(Notification.id))
                .group_by(Notification.type)
            )
            by_type = {ntype: count for ntype, count in type_result.all()}
            
            # Recent activity (last 24 hours)
            from datetime import timedelta
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_result = await session.execute(
                select(func.count(Notification.id))
                .where(Notification.created_at >= last_24h)
            )
            recent = recent_result.scalar()
            
            return {
                "total_notifications": total,
                "by_status": by_status,
                "by_type": by_type,
                "last_24h": recent,
            }
    
    # Convenience methods for common notification types
    
    async def notify_admin(self, title: str, message: str, admin_user_id: int) -> Notification:
        """Send notification to admin."""
        return await self.create_notification(
            title=title,
            message=message,
            notification_type=NotificationType.ADMIN,
            user_id=admin_user_id,
            priority=3
        )
    
    async def notify_error(self, title: str, message: str, user_id: Optional[int] = None) -> Notification:
        """Send error notification."""
        return await self.create_notification(
            title=title,
            message=message,
            notification_type=NotificationType.ERROR,
            user_id=user_id,
            priority=5
        )
    
    async def broadcast_announcement(self, title: str, message: str) -> Notification:
        """Send broadcast announcement."""
        return await self.create_notification(
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            is_broadcast=True,
            priority=2
        )
