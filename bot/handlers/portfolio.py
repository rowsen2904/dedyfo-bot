from aiogram.types import CallbackQuery

from bot import dp
from bot.keyboards import get_inline_keyboard
from bot.texts.info import Info


@dp.callback_query(lambda c: c.data == "portfolio")
async def portfolio_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        Info.PORTFOLIO,
        reply_markup=get_inline_keyboard(exclude="portfolio")
    )
