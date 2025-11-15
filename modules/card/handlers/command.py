import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.crud.user import UserDBCrud
from modules.card.keyboards.inline.buttons import menu_user

router = Router(name=__name__)
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def start_command(message: Message, db_session: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    
    user_db_crud = UserDBCrud(user_id, db_session)
    
    if await user_db_crud.update_create_user():
        await message.answer(
            text=
            f"Привет {message.from_user.full_name}!\n"
            "Меню:",
            reply_markup=menu_user(user_id)
        )
    else:
        await message.answer(
            text=
            "Ошибка"
        )