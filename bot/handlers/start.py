from aiogram.filters import CommandStart
from aiogram.types import Message

from bot import dp
from bot.keyboards import get_inline_keyboard


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Этот бот — моё интерактивное резюме. Здесь ты можешь узнать больше обо мне и получить мои контакты.",
        reply_markup=get_inline_keyboard()
    )
