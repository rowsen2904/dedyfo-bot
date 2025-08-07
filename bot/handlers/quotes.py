from aiogram.types import CallbackQuery

from bot import dp
from bot.api.quotes_client import QuotesAPIClient
from bot.config import Config
from bot.keyboards import get_inline_keyboard


@dp.callback_query(lambda c: c.data == "quotes")
async def quotes_callback_handler(callback: CallbackQuery) -> None:
    api_client = QuotesAPIClient(Config.QUOTES_API)
    quote = await api_client.get_quote()
    await callback.message.delete()
    await callback.message.answer(quote, reply_markup=get_inline_keyboard())
