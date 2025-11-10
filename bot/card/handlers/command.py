import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from bot.card.keyboards.inline.inline import menu_user
from kos_Htools import BaseDAO
from bot.shared.db.models.user import User
from config import is_admin

router = Router(name=__name__)
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def start_handler(message: Message, db_session: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user_dao = BaseDAO(User, db_session)
    
    update_create_data = {
        "user_id": user_id,
        "admin": is_admin(user_id)
    }
    
    user = await user_dao.get_one(User.user_id == user_id)
    
    if user:
        update = await user_dao.update(
            User.user_id == user_id,
            update_create_data
            )
        if not update:
            logger.error(f"Не обновился пользователь: {user_id}")
            return
    else:
        create = await user_dao.create(update_create_data)
        if not create:
            logger.error(f"Пользватель {user_id} не был добавлен в бд")
            return
    
    await message.answer(
        text=
        f"Привет {message.from_user.full_name}!\n"
        "Меню:",
        reply_markup=menu_user(user_id)
    )