"""About me handler with enhanced information."""

from aiogram.types import CallbackQuery

from ..keyboards.main_keyboard import get_main_keyboard
from ..texts.info import Info


async def about_me_callback_handler(callback: CallbackQuery, user=None, **kwargs) -> None:
    """Handle about me section."""
    
    # Enhanced about me with personalization
    about_text = Info.ABOUT_ME
    
    # Add personalized greeting if user exists
    if user and user.first_name:
        about_text = f"Привет, {user.first_name}! 👋\n\n" + about_text
    
    # Check if user is admin for proper keyboard
    is_admin = user and user.is_admin if user else False
    
    await callback.message.edit_text(
        about_text,
        reply_markup=get_main_keyboard(exclude="about_me", is_admin=is_admin),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()
