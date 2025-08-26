"""Analytics middleware for tracking user interactions."""

import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from ..core.dependencies import get_analytics_service
from ..database.models import ActionType

logger = logging.getLogger(__name__)


class AnalyticsMiddleware(BaseMiddleware):
    """Middleware for tracking user interactions and analytics."""
    
    def __init__(self) -> None:
        """Initialize analytics middleware."""
        super().__init__()
        self.action_mapping = {
            '/start': ActionType.START,
            '/help': ActionType.HELP,
            'about_me': ActionType.ABOUT,
            'portfolio': ActionType.PORTFOLIO,
            'quotes': ActionType.QUOTES,
            'weather': ActionType.WEATHER,
            'news': ActionType.NEWS,
            'admin_panel': ActionType.ADMIN_PANEL,
            'settings': ActionType.SETTINGS,
            'feedback': ActionType.FEEDBACK,
        }
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process analytics tracking."""
        
        # Start timing
        start_time = time.time()
        
        # Extract user info
        user_id = None
        action = None
        details = None
        chat_type = None
        message_type = None
        
        try:
            if isinstance(event, Message):
                user_id = event.from_user.id if event.from_user else None
                chat_type = event.chat.type
                message_type = event.content_type
                
                # Determine action from message text
                if event.text:
                    text = event.text.strip()
                    if text.startswith('/'):
                        command = text.split()[0]
                        action = self.action_mapping.get(command)
                        details = text
                    else:
                        # Regular message
                        details = f"Message: {text[:100]}..."
                
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id if event.from_user else None
                chat_type = event.message.chat.type if event.message else None
                message_type = "callback_query"
                
                # Determine action from callback data
                if event.data:
                    action = self.action_mapping.get(event.data)
                    details = event.data
            
            # Execute handler
            result = await handler(event, data)
            
            # Calculate response time
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Track analytics if we have user and action
            if user_id and action:
                try:
                    analytics_service = await get_analytics_service()
                    await analytics_service.track_action(
                        user_id=user_id,
                        action=action,
                        details=details,
                        chat_type=chat_type,
                        message_type=message_type,
                        response_time_ms=response_time_ms,
                    )
                except Exception as e:
                    logger.error(f"Failed to track analytics: {e}")
            
            return result
            
        except Exception as e:
            # Track error
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            if user_id:
                try:
                    analytics_service = await get_analytics_service()
                    await analytics_service.track_action(
                        user_id=user_id,
                        action=ActionType.ERROR,
                        details=f"Error: {str(e)[:200]}",
                        chat_type=chat_type,
                        message_type=message_type,
                        response_time_ms=response_time_ms,
                    )
                except Exception:
                    pass  # Don't let analytics errors break the handler
            
            raise
