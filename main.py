import asyncio

from bot import bot, dp
from bot.handlers import *


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
