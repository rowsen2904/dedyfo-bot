from aiogram.types import CallbackQuery

from bot import dp
from bot.config import Config
from bot.keyboards import get_inline_keyboard
from bot.usecases.quotes import get_translated_quote

@dp.callback_query(lambda c: c.data == "quotes")
async def quotes_callback_handler(callback: CallbackQuery) -> None:
    translated_quote = await get_translated_quote(Config.TRANSLATOR, 'ru')
    await callback.message.delete()
    await callback.message.answer(translated_quote, reply_markup=get_inline_keyboard())
