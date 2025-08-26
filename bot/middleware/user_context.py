"""User context middleware for automatic user management."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, User as TgUser

from ..core.dependencies import get_user_service
from ..database.models import User

logger = logging.getLogger(__name__)


class UserContextMiddleware(BaseMiddleware):
    """Middleware to manage user context and automatic user creation/updates."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process user context."""
        
        # Extract user from different event types
        tg_user: TgUser = None
        
        if hasattr(event, 'from_user') and event.from_user:
            tg_user = event.from_user
        elif hasattr(event, 'message') and event.message and event.message.from_user:
            tg_user = event.message.from_user
        
        if tg_user and not tg_user.is_bot:
            try:
                user_service = await get_user_service()
                
                # Get or create user in database
                user = await user_service.get_or_create_user(
                    user_id=tg_user.id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                    last_name=tg_user.last_name,
                    language_code=tg_user.language_code,
                    is_premium=getattr(tg_user, 'is_premium', None),
                )
                
                # Add user to context
                data['user'] = user
                data['tg_user'] = tg_user
                
                # Update last interaction
                await user_service.update_last_interaction(tg_user.id)
                
                # Increment message count for messages
                if hasattr(event, 'text') or hasattr(event, 'caption'):
                    await user_service.increment_message_count(tg_user.id)
                
                logger.debug(f"User context set for {user.full_name} (ID: {tg_user.id})")
                
            except Exception as e:
                logger.error(f"Error setting user context for {tg_user.id}: {e}")
                # Continue without user context
                pass
        
        return await handler(event, data)
