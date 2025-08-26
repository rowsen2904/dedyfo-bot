"""Advanced keyboard layouts for the bot."""

from typing import List, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from ..core.dependencies import get_container


def get_main_keyboard(exclude: Optional[str] = None, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Get main navigation keyboard."""
    buttons = []

    # Main features
    if exclude != "about_me":
        buttons.append([InlineKeyboardButton(
            text="👤 Обо мне", callback_data="about_me")])

    if exclude != "portfolio":
        buttons.append([InlineKeyboardButton(
            text="💼 Портфолио", callback_data="portfolio")])

    # New features row
    feature_row = []
    if exclude != "quotes":
        feature_row.append(InlineKeyboardButton(
            text="💬 Цитаты", callback_data="quotes"))
    
    if exclude != "weather":
        feature_row.append(InlineKeyboardButton(
            text="🌤 Погода", callback_data="weather"))
    
    if feature_row:
        buttons.append(feature_row)

    # Tools row
    tools_row = []
    if exclude != "news":
        tools_row.append(InlineKeyboardButton(
            text="📰 Новости", callback_data="news"))
    
    if exclude != "crypto":
        tools_row.append(InlineKeyboardButton(
            text="₿ Крипто", callback_data="crypto"))
    
    if tools_row:
        buttons.append(tools_row)

    # Entertainment row
    fun_row = []
    if exclude != "joke":
        fun_row.append(InlineKeyboardButton(
            text="😄 Шутка", callback_data="joke"))
    
    if exclude != "cat_fact":
        fun_row.append(InlineKeyboardButton(
            text="🐱 Факт о котах", callback_data="cat_fact"))
    
    if fun_row:
        buttons.append(fun_row)

    # Settings and feedback
    if exclude != "settings":
        buttons.append([InlineKeyboardButton(
            text="⚙️ Настройки", callback_data="settings")])

    # Admin panel for admins
    if is_admin and exclude != "admin_panel":
        buttons.append([InlineKeyboardButton(
            text="🔧 Админ-панель", callback_data="admin_panel")])

    # Back button
    if exclude:
        buttons.append([InlineKeyboardButton(
            text="🔄 Назад", callback_data="back")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_weather_keyboard() -> InlineKeyboardMarkup:
    """Get weather selection keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="🌍 Москва", callback_data="weather:Moscow"),
            InlineKeyboardButton(text="🌆 Ашхабад", callback_data="weather:Ashgabat"),
        ],
        [
            InlineKeyboardButton(text="🗽 Нью-Йорк", callback_data="weather:New York"),
            InlineKeyboardButton(text="🗼 Париж", callback_data="weather:Paris"),
        ],
        [
            InlineKeyboardButton(text="🏙 Лондон", callback_data="weather:London"),
            InlineKeyboardButton(text="🌸 Токио", callback_data="weather:Tokyo"),
        ],
        [InlineKeyboardButton(text="📍 Свой город", callback_data="weather:custom")],
        [InlineKeyboardButton(text="🔄 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_news_keyboard() -> InlineKeyboardMarkup:
    """Get news categories keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="📈 Бизнес", callback_data="news:business"),
            InlineKeyboardButton(text="💻 Технологии", callback_data="news:technology"),
        ],
        [
            InlineKeyboardButton(text="⚽ Спорт", callback_data="news:sports"),
            InlineKeyboardButton(text="🎭 Развлечения", callback_data="news:entertainment"),
        ],
        [
            InlineKeyboardButton(text="🔬 Наука", callback_data="news:science"),
            InlineKeyboardButton(text="💊 Здоровье", callback_data="news:health"),
        ],
        [InlineKeyboardButton(text="📰 Общие", callback_data="news:general")],
        [InlineKeyboardButton(text="🔄 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Get admin panel keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"),
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin:users"),
        ],
        [
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin:broadcast"),
            InlineKeyboardButton(text="📋 Логи", callback_data="admin:logs"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Система", callback_data="admin:system"),
            InlineKeyboardButton(text="🗄 База данных", callback_data="admin:database"),
        ],
        [InlineKeyboardButton(text="🔄 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Get user settings keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="🌐 Язык", callback_data="settings:language"),
            InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings:notifications"),
        ],
        [
            InlineKeyboardButton(text="📊 Моя статистика", callback_data="settings:my_stats"),
            InlineKeyboardButton(text="📝 Обратная связь", callback_data="settings:feedback"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="settings:about_bot"),
            InlineKeyboardButton(text="❓ Помощь", callback_data="settings:help"),
        ],
        [InlineKeyboardButton(text="🔄 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Get confirmation keyboard for dangerous actions."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm:{action}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str
) -> InlineKeyboardMarkup:
    """Get pagination keyboard."""
    buttons = []
    
    # Navigation row
    nav_row = []
    if current_page > 1:
        nav_row.append(InlineKeyboardButton(
            text="⬅️", callback_data=f"{callback_prefix}:page:{current_page - 1}"
        ))
    
    nav_row.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}", callback_data="noop"
    ))
    
    if current_page < total_pages:
        nav_row.append(InlineKeyboardButton(
            text="➡️", callback_data=f"{callback_prefix}:page:{current_page + 1}"
        ))
    
    buttons.append(nav_row)
    
    # Back button
    buttons.append([InlineKeyboardButton(text="🔄 Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Legacy function for backward compatibility
def get_inline_keyboard(exclude: Optional[str] = None) -> InlineKeyboardMarkup:
    """Legacy function - use get_main_keyboard instead."""
    return get_main_keyboard(exclude=exclude)
