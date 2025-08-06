from aiogram.types import CallbackQuery

from bot import dp
from bot.keyboards import get_inline_keyboard
from bot.texts.info import Info


@dp.callback_query(lambda c: c.data == "about_me")
async def about_me_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        Info.ABOUT_ME,
        reply_markup=get_inline_keyboard(exclude="about_me")
    )
