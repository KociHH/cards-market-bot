import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
import asyncio
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from bot.admin.keyboards.inline.inline import admin_menu_bt, back_admin_menu_bt
from bot.admin.keyboards.reply.button_names import AdminMenu, ChangeCard
from bot.admin.keyboards.reply.reply import back_menu_admin_reply_bt
from bot.admin.keyboards.reply.states import ChangeCardState
from bot.admin.db.models.admin import OnModeration
from bot.shared.db.models.user import User
from config import is_admin

router = Router(name=__name__)
logger = logging.getLogger(__name__)

@router.message(
    F.text.in_([ChangeCard.name, ChangeCard.description]), 
    StateFilter(ChangeCardState.change_)
    )
async def change_card_process(message: Message, state: FSMContext):
    data = await state.get_data()
    text = message.text
    
    name = data.get("name")
    description = data.get("description")
    
    if text == ChangeCard.name:
        await message.answer(
            text=
            f"Текущее название: {name}\n"
            "Введите новое название:"
        )
        await state.set_state(ChangeCardState.name)
       
    elif text == ChangeCard.description:
        await message.answer(
            text=
            f"Текущее описание: {description}\n"
            "Введите новое описание:"
        )
        await state.set_state(ChangeCardState.description)
        
@router.message(StateFilter(ChangeCardState.name, ChangeCardState.description))
async def change_name_description(message: Message, state: FSMContext, db_session: AsyncSession):
    current_state = await state.get_state()
    data = await state.get_data()
    text = message.text
    moder_dao = BaseDAO(OnModeration, db_session)
    
    card_id = data.get("card_id")
    if not card_id:
        logger.error(f"Не найден параметр card_id в данных состояния: {data}")
        await message.answer("Ошибка: не найден ID карточки. Вернитесь в меню.")
        return
    
    if current_state == ChangeCardState.name:
        update_result = await moder_dao.update(
            OnModeration.id == card_id,
            {"name": text}
        )
        if not update_result:
            logger.error(f"Не получилось обновить название карточки {card_id}")
            await message.answer("Ошибка при обновлении названия")
            return
        
        await message.answer(
            f"Успешно было изменено название на '{text}'! Продолжайте изменять, либо вернитесь обратно в меню",
            reply_markup=back_admin_menu_bt()
        )
        data["name"] = text
        await state.set_data(data)
        
    elif current_state == ChangeCardState.description:
        update_result = await moder_dao.update(
            OnModeration.id == card_id,
            {"description": text}
        )
        if not update_result:
            logger.error(f"Не получилось обновить описание карточки {card_id}")
            await message.answer("Ошибка при обновлении описания")
            return
        
        await message.answer(
            f"Успешно было изменено описание на '{text}'! Продолжайте изменять, либо вернитесь обратно в меню",
            reply_markup=back_admin_menu_bt()
        )
        data["description"] = text
        await state.set_data(data)
        
    await state.set_state(ChangeCardState.change_)
        
@router.message(F.text == AdminMenu.back_admin_menu)
async def back_card_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.edit_text(
        text="Меню админа:",
        reply_markup=admin_menu_bt()
    )