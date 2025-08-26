"""Authentication middleware for admin access control."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from ..core.dependencies import get_container

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware for authentication and authorization."""
    
    def __init__(self) -> None:
        """Initialize auth middleware."""
        super().__init__()
        self.admin_only_commands = {
            '/admin', '/stats', '/broadcast', '/users', '/logs',
            'admin_panel', 'user_stats', 'system_stats', 'send_broadcast'
        }
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Check authentication and authorization."""
        
        # Extract user info
        user_id = None
        command_or_callback = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            if event.text and event.text.startswith('/'):
                command_or_callback = event.text.split()[0]
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            command_or_callback = event.data
        
        # Check if this is an admin-only action
        if command_or_callback and command_or_callback in self.admin_only_commands:
            if not user_id:
                logger.warning("Admin action attempted without user ID")
                return None
            
            try:
                # Check if user is admin
                container = get_container()
                settings = container.settings
                
                # Check against configured admin IDs
                is_admin = user_id in settings.admin.admin_user_ids
                is_super_admin = user_id == settings.admin.super_admin_id
                
                # Also check database admin status
                user = data.get('user')
                is_db_admin = user and user.is_admin
                
                if not (is_admin or is_super_admin or is_db_admin):
                    logger.warning(f"Non-admin user {user_id} attempted admin action: {command_or_callback}")
                    
                    # Send access denied message
                    try:
                        if isinstance(event, Message):
                            await event.answer("🚫 У вас нет прав для выполнения этой команды.")
                        elif isinstance(event, CallbackQuery):
                            await event.answer("🚫 У вас нет прав для выполнения этого действия.", show_alert=True)
                    except Exception as e:
                        logger.error(f"Error sending access denied message: {e}")
                    
                    return None  # Block the request
                
                # Add admin flags to context
                data['is_admin'] = True
                data['is_super_admin'] = is_super_admin
                
                logger.debug(f"Admin access granted for user {user_id}: {command_or_callback}")
                
            except Exception as e:
                logger.error(f"Error in auth middleware for user {user_id}: {e}")
                # Deny access on errors for security
                return None
        
        return await handler(event, data)
