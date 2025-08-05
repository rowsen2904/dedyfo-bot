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
        [InlineKeyboardButton(text="🔍 Обо мне", callback_data="about_me")],
        [InlineKeyboardButton(text="💼 Портфолио", callback_data="portfolio")]
    ]
)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Этот бот — моё интерактивное резюме. Здесь ты можешь узнать больше обо мне и получить мои контакты.",
        reply_markup=inline_keyboard
    )


@dp.callback_query(lambda c: c.data == "about_me")
async def about_me_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        Info.ABOUT_ME,
        reply_markup=inline_keyboard
    )


@dp.callback_query(lambda c: c.data == "portfolio")
async def portfolio_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        Info.PORTFOLIO,
        reply_markup=inline_keyboard
    )


async def main():
    bot = Bot(
        token=Config.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
