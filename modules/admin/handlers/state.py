import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.keyboards.inline.buttons import admin_menu_bt, back_admin_menu_bt
from modules.admin.keyboards.reply.button_names import AdminMenu, ChangeCard
from modules.admin.keyboards.reply.states import ChangeCardState
from modules.admin.services.moder_card.service import ModerCardService

router = Router(name=__name__)
logger = logging.getLogger(__name__)

moder_card_service = ModerCardService()

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
    
    card_id = data.get("card_id")
    if not card_id:
        logger.error(f"Не найден параметр card_id в данных состояния: {data}")
        await message.answer("Ошибка: не найден ID карточки. Вернитесь в меню")
        return
    
    if current_state == ChangeCardState.name:
        result_name_description = await moder_card_service.change.handle_name_description(db_session, card_id, ChangeCardState.name, text)
        
        await result_name_description.message_answer(message)
        
        if result_name_description.is_error:
            return
        
        data["name"] = text
        await state.set_data(data)
        
    elif current_state == ChangeCardState.description:
        result_name_description = await moder_card_service.change.handle_name_description(db_session, card_id, ChangeCardState.description, text)
        
        await result_name_description.message_answer(message)
        
        if result_name_description.is_error:
            return
        
        data["description"] = text
        await state.set_data(data)
        
    await state.set_state(ChangeCardState.change_)
        
@router.message(F.text == AdminMenu.back_admin_menu)
async def back_card_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Меню админа:",
        reply_markup=admin_menu_bt()
    )