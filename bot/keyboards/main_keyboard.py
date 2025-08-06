from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_inline_keyboard(exclude: str = None) -> InlineKeyboardMarkup:
    buttons = []

    if exclude != "about_me":
        buttons.append([InlineKeyboardButton(
            text="🔍 Обо мне", callback_data="about_me")])

    if exclude != "portfolio":
        buttons.append([InlineKeyboardButton(
            text="💼 Портфолио", callback_data="portfolio")])

    if exclude:
        buttons.append([InlineKeyboardButton(
            text="🔄 Назад", callback_data="back")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
