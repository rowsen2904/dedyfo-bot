import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.enums import ParseMode

from config import Config
from info import Info

dp = Dispatcher()


inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Обо мне", callback_data="about_me")]
    ]
)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Hello! I'm a bot created with aiogram.", reply_markup=inline_keyboard)


@dp.callback_query(lambda c: c.data == "about_me")
async def about_me_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.answer(Info.ABOUT_ME)


async def main():
    bot = Bot(
        token=Config.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
