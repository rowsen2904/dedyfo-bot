"""Start command handler with enhanced welcome message."""

from aiogram.filters import CommandStart
from aiogram.types import Message

from ..keyboards.main_keyboard import get_main_keyboard


async def command_start_handler(message: Message, user=None, **kwargs) -> None:
    """Handle /start command with personalized welcome."""
    
    # Personalized greeting
    if user:
        if user.first_name:
            greeting = f"Привет, {user.first_name}!"
        else:
            greeting = "Привет!"
    else:
        greeting = "Привет!"
    
    # Check if this is a returning user
    is_returning = user and user.total_messages > 1 if user else False
    
    if is_returning:
        welcome_text = (
            f"{greeting}\n\n"
            "🎉 Рад видеть тебя снова!\n\n"
            "Этот бот — моё интерактивное резюме. Здесь ты можешь:\n"
            "👤 Узнать больше обо мне\n"
            "💼 Посмотреть портфолио\n"
            "🌤 Узнать погоду\n"
            "📰 Почитать новости\n"
            "💬 Получить мотивирующие цитаты\n"
            "😄 Развлечься шутками и фактами\n\n"
            "Что будем делать?"
        )
    else:
        welcome_text = (
            f"{greeting}\n\n"
            "🤖 Добро пожаловать в мой интерактивный бот-резюме!\n\n"
            "Я — <b>Ровшен Байрамов</b>, Backend-разработчик.\n"
            "Этот бот покажет мои навыки на практике.\n\n"
            "🚀 <b>Что можно сделать:</b>\n"
            "👤 Узнать обо мне и моем опыте\n"
            "💼 Посмотреть проекты и достижения\n"
            "🌐 Воспользоваться полезными функциями\n"
            "🎮 Развлечься интересным контентом\n\n"
            "Выбери интересующий раздел ⬇️"
        )
    
    # Check if user is admin
    is_admin = user and user.is_admin if user else False
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(is_admin=is_admin),
        parse_mode="HTML"
    )
