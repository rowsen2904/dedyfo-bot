"""Enhanced quotes handler with caching and error handling."""

import logging
from aiogram.types import CallbackQuery

from ..core.dependencies import get_cache_service, get_external_api_service
from ..keyboards.main_keyboard import get_main_keyboard

logger = logging.getLogger(__name__)


async def quotes_callback_handler(callback: CallbackQuery, user=None, **kwargs) -> None:
    """Handle quotes request with caching and enhanced formatting."""
    try:
        # Show loading
        await callback.message.edit_text("🔄 Подбираю вдохновляющую цитату...")
        
        # Try to get cached quote first
        cache_service = await get_cache_service()
        cached_quote = await cache_service.get_cached_quote()
        
        if cached_quote:
            quote_data = cached_quote
        else:
            # Get new quote from API
            external_api = await get_external_api_service()
            quote_data = await external_api.get_quote()
            
            if quote_data:
                # Cache the quote
                await cache_service.cache_quote(quote_data)
        
        if quote_data:
            # Format quote nicely
            quote_text = (
                f"💫 <b>Цитата дня</b>\n\n"
                f"<i>"{quote_data['text']}"</i>\n\n"
                f"— <b>{quote_data['author']}</b>"
            )
            
            # Add tags if available
            if quote_data.get('tags'):
                tags_text = ", ".join(f"#{tag}" for tag in quote_data['tags'][:3])
                quote_text += f"\n\n🏷 {tags_text}"
        else:
            quote_text = (
                "❌ Не удалось получить цитату.\n\n"
                "💡 Вот цитата от меня:\n"
                "<i>\"Каждый день — это возможность стать лучше!\"</i>\n\n"
                "— Ровшен Байрамов"
            )
        
        # Check if user is admin for proper keyboard
        is_admin = user and user.is_admin if user else False
        
        await callback.message.edit_text(
            quote_text,
            reply_markup=get_main_keyboard(exclude="quotes", is_admin=is_admin),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error handling quotes: {e}")
        
        # Fallback quote
        fallback_text = (
            "💫 <b>Цитата дня</b>\n\n"
            "<i>\"Лучший способ предсказать будущее — создать его.\"</i>\n\n"
            "— Питер Друкер"
        )
        
        is_admin = user and user.is_admin if user else False
        
        await callback.message.edit_text(
            fallback_text,
            reply_markup=get_main_keyboard(exclude="quotes", is_admin=is_admin),
            parse_mode="HTML"
        )
    
    await callback.answer()
