from aiogram.types import CallbackQuery

from bot import dp
from bot.keyboards import get_inline_keyboard


@dp.callback_query(lambda c: c.data == "back")
async def back_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        "Привет! Этот бот — моё интерактивное резюме. Здесь ты можешь узнать больше обо мне и получить мои контакты.",
        reply_markup=get_inline_keyboard()
    )
