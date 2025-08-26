"""Analytics service for tracking user actions and generating insights."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import Analytics, ActionType, DatabaseManager, User
from .base import BaseService

logger = logging.getLogger(__name__)


class AnalyticsService(BaseService[Analytics]):
    """Service for analytics and user behavior tracking."""
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize analytics service."""
        super().__init__(Analytics, db_manager)
    
    async def track_action(
        self,
        user_id: int,
        action: ActionType,
        details: Optional[str] = None,
        chat_type: Optional[str] = None,
        message_type: Optional[str] = None,
        response_time_ms: Optional[int] = None,
    ) -> Analytics:
        """Track user action."""
        async with self.db_manager.get_session() as session:
            analytics_entry = await self.create(
                session,
                user_id=user_id,
                action=action,
                details=details,
                chat_type=chat_type,
                message_type=message_type,
                response_time_ms=response_time_ms,
            )
            logger.debug(f"Tracked action {action} for user {user_id}")
            return analytics_entry
    
    async def get_user_actions(
        self, 
        user_id: int, 
        limit: int = 50,
        action_type: Optional[ActionType] = None
    ) -> List[Analytics]:
        """Get user's recent actions."""
        async with self.db_manager.get_session() as session:
            query = select(Analytics).where(Analytics.user_id == user_id)
            
            if action_type:
                query = query.where(Analytics.action == action_type)
            
            query = query.order_by(Analytics.created_at.desc()).limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_action_stats(
        self, 
        days: int = 7
    ) -> Dict[str, int]:
        """Get action statistics for the last N days."""
        async with self.db_manager.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(Analytics.action, func.count(Analytics.id))
                .where(Analytics.created_at >= cutoff_date)
                .group_by(Analytics.action)
                .order_by(func.count(Analytics.id).desc())
            )
            
            return {action: count for action, count in result.all()}
    
    async def get_daily_stats(self, days: int = 30) -> List[Dict]:
        """Get daily usage statistics."""
        async with self.db_manager.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(
                    func.date(Analytics.created_at).label('date'),
                    func.count(Analytics.id).label('total_actions'),
                    func.count(func.distinct(Analytics.user_id)).label('unique_users')
                )
                .where(Analytics.created_at >= cutoff_date)
                .group_by(func.date(Analytics.created_at))
                .order_by(func.date(Analytics.created_at))
            )
            
            return [
                {
                    "date": row.date,
                    "total_actions": row.total_actions,
                    "unique_users": row.unique_users
                }
                for row in result.all()
            ]
    
    async def get_user_engagement_stats(self) -> Dict:
        """Get user engagement statistics."""
        async with self.db_manager.get_session() as session:
            # Total actions
            total_actions = await session.execute(
                select(func.count(Analytics.id))
            )
            total_actions = total_actions.scalar()
            
            # Unique users with actions
            unique_users = await session.execute(
                select(func.count(func.distinct(Analytics.user_id)))
            )
            unique_users = unique_users.scalar()
            
            # Average actions per user
            avg_actions = total_actions / unique_users if unique_users > 0 else 0
            
            # Most active users
            most_active = await session.execute(
                select(
                    Analytics.user_id,
                    func.count(Analytics.id).label('action_count'),
                    User.first_name,
                    User.username
                )
                .join(User, Analytics.user_id == User.id)
                .group_by(Analytics.user_id, User.first_name, User.username)
                .order_by(func.count(Analytics.id).desc())
                .limit(10)
            )
            
            most_active_users = [
                {
                    "user_id": row.user_id,
                    "action_count": row.action_count,
                    "name": row.first_name or row.username or f"User_{row.user_id}"
                }
                for row in most_active.all()
            ]
            
            # Recent activity (last 24 hours)
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_activity = await session.execute(
                select(func.count(Analytics.id))
                .where(Analytics.created_at >= last_24h)
            )
            recent_activity = recent_activity.scalar()
            
            return {
                "total_actions": total_actions,
                "unique_users": unique_users,
                "average_actions_per_user": round(avg_actions, 2),
                "most_active_users": most_active_users,
                "last_24h_activity": recent_activity,
            }
    
    async def get_popular_features(self, days: int = 30) -> List[Dict]:
        """Get most popular features based on usage."""
        async with self.db_manager.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(
                    Analytics.action,
                    func.count(Analytics.id).label('usage_count'),
                    func.count(func.distinct(Analytics.user_id)).label('unique_users'),
                    func.avg(Analytics.response_time_ms).label('avg_response_time')
                )
                .where(Analytics.created_at >= cutoff_date)
                .group_by(Analytics.action)
                .order_by(func.count(Analytics.id).desc())
            )
            
            return [
                {
                    "feature": row.action,
                    "usage_count": row.usage_count,
                    "unique_users": row.unique_users,
                    "avg_response_time_ms": round(row.avg_response_time, 2) if row.avg_response_time else None
                }
                for row in result.all()
            ]
    
    async def get_user_journey(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's journey through the bot."""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(Analytics)
                .where(Analytics.user_id == user_id)
                .order_by(Analytics.created_at.desc())
                .limit(limit)
            )
            
            actions = result.scalars().all()
            return [
                {
                    "action": action.action,
                    "timestamp": action.created_at,
                    "details": action.details,
                    "response_time_ms": action.response_time_ms
                }
                for action in actions
            ]
    
    async def get_performance_metrics(self, days: int = 7) -> Dict:
        """Get performance metrics."""
        async with self.db_manager.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Average response time
            avg_response_time = await session.execute(
                select(func.avg(Analytics.response_time_ms))
                .where(
                    and_(
                        Analytics.created_at >= cutoff_date,
                        Analytics.response_time_ms.is_not(None)
                    )
                )
            )
            avg_response_time = avg_response_time.scalar()
            
            # Response time percentiles
            response_times = await session.execute(
                select(Analytics.response_time_ms)
                .where(
                    and_(
                        Analytics.created_at >= cutoff_date,
                        Analytics.response_time_ms.is_not(None)
                    )
                )
                .order_by(Analytics.response_time_ms)
            )
            
            times = [time for time, in response_times.all()]
            
            def percentile(data, p):
                if not data:
                    return None
                k = (len(data) - 1) * p / 100
                f = int(k)
                c = k - f
                if f == len(data) - 1:
                    return data[f]
                return data[f] * (1 - c) + data[f + 1] * c
            
            return {
                "avg_response_time_ms": round(avg_response_time, 2) if avg_response_time else None,
                "p50_response_time_ms": percentile(times, 50),
                "p95_response_time_ms": percentile(times, 95),
                "p99_response_time_ms": percentile(times, 99),
                "total_requests": len(times),
            }
    
    async def cleanup_old_data(self, days: int = 90) -> int:
        """Clean up analytics data older than specified days."""
        async with self.db_manager.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await session.execute(
                select(func.count(Analytics.id))
                .where(Analytics.created_at < cutoff_date)
            )
            count_to_delete = result.scalar()
            
            if count_to_delete > 0:
                await session.execute(
                    Analytics.__table__.delete()
                    .where(Analytics.created_at < cutoff_date)
                )
                logger.info(f"Cleaned up {count_to_delete} old analytics records")
            
            return count_to_delete
