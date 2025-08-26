"""User service for managing user data and interactions."""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import DatabaseManager, User, UserStatus
from .base import BaseService

logger = logging.getLogger(__name__)


class UserService(BaseService[User]):
    """Service for user management."""
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize user service."""
        super().__init__(User, db_manager)
    
    async def get_or_create_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None,
        is_premium: Optional[bool] = None,
    ) -> User:
        """Get existing user or create new one."""
        async with self.db_manager.get_session() as session:
            # Try to get existing user
            user = await self.get_by_id(session, user_id)
            
            if user is None:
                # Create new user
                user = await self.create(
                    session,
                    id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code=language_code,
                    is_premium=is_premium,
                )
                logger.info(f"Created new user: {user.full_name} (ID: {user_id})")
            else:
                # Update existing user info
                updates = {}
                if username is not None and user.username != username:
                    updates["username"] = username
                if first_name is not None and user.first_name != first_name:
                    updates["first_name"] = first_name
                if last_name is not None and user.last_name != last_name:
                    updates["last_name"] = last_name
                if language_code is not None and user.language_code != language_code:
                    updates["language_code"] = language_code
                if is_premium is not None and user.is_premium != is_premium:
                    updates["is_premium"] = is_premium
                
                if updates:
                    user = await self.update(session, user, **updates)
                    logger.debug(f"Updated user info: {user.full_name} (ID: {user_id})")
            
            return user
    
    async def update_last_interaction(self, user_id: int) -> None:
        """Update user's last interaction timestamp."""
        async with self.db_manager.get_session() as session:
            user = await self.get_by_id(session, user_id)
            if user:
                await self.update(
                    session, 
                    user, 
                    last_interaction=datetime.utcnow()
                )
    
    async def increment_message_count(self, user_id: int) -> None:
        """Increment user's message count."""
        async with self.db_manager.get_session() as session:
            user = await self.get_by_id(session, user_id)
            if user:
                await self.update(
                    session,
                    user,
                    total_messages=user.total_messages + 1
                )
    
    async def set_admin_status(self, user_id: int, is_admin: bool) -> bool:
        """Set user admin status."""
        async with self.db_manager.get_session() as session:
            user = await self.get_by_id(session, user_id)
            if user:
                await self.update(session, user, is_admin=is_admin)
                logger.info(f"Updated admin status for user {user_id}: {is_admin}")
                return True
            return False
    
    async def set_user_status(self, user_id: int, status: UserStatus) -> bool:
        """Set user status."""
        async with self.db_manager.get_session() as session:
            user = await self.get_by_id(session, user_id)
            if user:
                await self.update(session, user, status=status)
                logger.info(f"Updated status for user {user_id}: {status}")
                return True
            return False
    
    async def get_active_users(self, limit: int = 100) -> List[User]:
        """Get list of active users."""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(User)
                .where(User.status == UserStatus.ACTIVE)
                .order_by(User.last_interaction.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
    
    async def get_admin_users(self) -> List[User]:
        """Get list of admin users."""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                select(User)
                .where(User.is_admin == True)
                .order_by(User.first_name)
            )
            return list(result.scalars().all())
    
    async def get_user_stats(self) -> dict:
        """Get user statistics."""
        async with self.db_manager.get_session() as session:
            # Total users
            total_result = await session.execute(select(func.count(User.id)))
            total_users = total_result.scalar()
            
            # Active users
            active_result = await session.execute(
                select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
            )
            active_users = active_result.scalar()
            
            # New users today
            today = datetime.utcnow().date()
            new_today_result = await session.execute(
                select(func.count(User.id)).where(
                    func.date(User.created_at) == today
                )
            )
            new_today = new_today_result.scalar()
            
            # Premium users
            premium_result = await session.execute(
                select(func.count(User.id)).where(User.is_premium == True)
            )
            premium_users = premium_result.scalar()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "new_today": new_today,
                "premium_users": premium_users,
                "blocked_users": total_users - active_users,
            }
    
    async def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Search users by name or username."""
        async with self.db_manager.get_session() as session:
            search_pattern = f"%{query}%"
            result = await session.execute(
                select(User)
                .where(
                    (User.first_name.ilike(search_pattern)) |
                    (User.last_name.ilike(search_pattern)) |
                    (User.username.ilike(search_pattern))
                )
                .order_by(User.last_interaction.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
