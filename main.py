import asyncio
import logging
from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from middlewares.session import DBSessionMiddleware
from db.settings import create_tables
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from db.settings import async_session
from aiogram import Dispatcher
from modules.shared import handlers as shared_callback
from modules.admin import handlers as admin_callback
from modules.card import handlers as card_callback


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.update.middleware(DBSessionMiddleware(async_session))


async def main():
    dp.include_routers(admin_callback.router, card_callback.router, shared_callback.router)
    await create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

