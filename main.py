import asyncio
import logging
from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from bot.shared.middlewares.session import DBSessionMiddleware
from bot.shared.db.settings import create_tables
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.card.handlers import router as card_router
from bot.admin.handlers import router as admin_router
from bot.shared.handlers import router as shared_router
from bot.shared.db.settings import async_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.update.middleware(DBSessionMiddleware(async_session))
dp.include_routers(card_router, admin_router, shared_router)

if __name__ == "__main__":
    asyncio.run(create_tables())
    asyncio.run(dp.start_polling(bot))
