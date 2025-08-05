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


def get_inline_keyboard(exclude: str = None) -> InlineKeyboardMarkup:
    buttons = []

    if exclude != "about_me":
        buttons.append([InlineKeyboardButton(
            text="🔍 Обо мне", callback_data="about_me")])

    if exclude != "portfolio":
        buttons.append([InlineKeyboardButton(
            text="💼 Портфолио", callback_data="portfolio")])

    if exclude:
        buttons.append([InlineKeyboardButton(
            text="🔄 Назад", callback_data="back")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Этот бот — моё интерактивное резюме. Здесь ты можешь узнать больше обо мне и получить мои контакты.",
        reply_markup=get_inline_keyboard()
    )


@dp.callback_query(lambda c: c.data == "about_me")
async def about_me_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        Info.ABOUT_ME,
        reply_markup=get_inline_keyboard(exclude="about_me")
    )


@dp.callback_query(lambda c: c.data == "portfolio")
async def portfolio_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        Info.PORTFOLIO,
        reply_markup=get_inline_keyboard(exclude="portfolio")
    )


@dp.callback_query(lambda c: c.data == "back")
async def back_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        "Привет! Этот бот — моё интерактивное резюме. Здесь ты можешь узнать больше обо мне и получить мои контакты.",
        reply_markup=get_inline_keyboard()
    )


async def main():
    bot = Bot(
        token=Config.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
