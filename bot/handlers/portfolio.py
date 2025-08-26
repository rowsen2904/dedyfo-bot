"""Portfolio handler with enhanced project showcase."""

from aiogram.types import CallbackQuery

from ..keyboards.main_keyboard import get_main_keyboard
from ..texts.info import Info


async def portfolio_callback_handler(callback: CallbackQuery, user=None, **kwargs) -> None:
    """Handle portfolio section."""
    
    # Check if user is admin for proper keyboard
    is_admin = user and user.is_admin if user else False
    
    await callback.message.edit_text(
        Info.PORTFOLIO,
        reply_markup=get_main_keyboard(exclude="portfolio", is_admin=is_admin),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()
