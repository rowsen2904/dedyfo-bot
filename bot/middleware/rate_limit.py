"""Rate limiting middleware."""

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from ..core.dependencies import get_cache_service, get_container

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting user requests."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Apply rate limiting."""
        
        # Extract user ID
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message and event.message.from_user:
            user_id = event.message.from_user.id
        
        if user_id:
            try:
                # Get rate limit settings
                container = get_container()
                settings = container.settings
                
                # Check if user is admin (admins bypass rate limits)
                user = data.get('user')
                if user and user.is_admin:
                    return await handler(event, data)
                
                # Apply rate limiting
                cache_service = await get_cache_service()
                
                # Check rate limit
                allowed = await cache_service.set_rate_limit(
                    user_id=user_id,
                    limit=settings.bot.rate_limit_requests,
                    window=settings.bot.rate_limit_window
                )
                
                if not allowed:
                    # Rate limit exceeded
                    logger.warning(f"Rate limit exceeded for user {user_id}")
                    
                    # Try to send rate limit message (don't fail if we can't)
                    try:
                        from aiogram.types import Message
                        if isinstance(event, Message):
                            await event.answer(
                                "🚫 Слишком много запросов. Пожалуйста, подождите немного.",
                                show_alert=True
                            )
                    except Exception:
                        pass
                    
                    return None  # Don't process the request
                
            except Exception as e:
                logger.error(f"Error in rate limiting for user {user_id}: {e}")
                # Continue processing on rate limit errors
                pass
        
        return await handler(event, data)
