import logging
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
import asyncio
from kos_Htools import BaseDAO
from sqlalchemy import and_
from bot.admin.crud.user import create_update_statistic
from bot.admin.keyboards.inline.callback_data import AdminMenu, ApplicationsUsers, ModerCard, Slider
from sqlalchemy.ext.asyncio import AsyncSession
from bot.admin.keyboards.inline.inline import admin_menu_bt, applications_slider_bt, back_admin_menu_bt, moder_slider_bt, statistic_slider_bt
from bot.admin.crud.utils import slider_pages
from bot.admin.keyboards.reply.button_names import ChangeCard
from bot.admin.keyboards.reply.reply import change_card_bt
from bot.admin.keyboards.reply.states import ChangeCardState
from bot.admin.db.models.admin import Applications, OnModeration, Statistics
from bot.card.db.models.card import Card
from bot.shared.crud.utils import slice_page_num
from bot.shared.db.models.user import Balance

router = Router(name=__name__)
logger = logging.getLogger(__name__)

@router.callback_query(F.data == AdminMenu.admin)
async def admin_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        text="Меню админа:",
        reply_markup=admin_menu_bt()
    )

@router.callback_query(F.data == AdminMenu.moder)
async def moder(call: CallbackQuery, db_session: AsyncSession):
    page = 1
    result = await slider_pages("moder", page, db_session)
    if result and isinstance(result, tuple) and len(result) == 3:
        result_text, user_id, card_id = result
        if result_text and user_id and card_id:
            await call.message.edit_text(
                result_text, 
                reply_markup=moder_slider_bt(page, user_id, card_id)
                )
            return
    await call.answer("Нет карточек для проверки")
      
@router.callback_query(F.data.startswith(ModerCard.add))
async def add_card(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # add_card-{page}-{user_id}-{card_id}
    data = call.data.split("-")
    if len(data) < 4:
        logger.error(f"Неправильный размер данных для кнопки добавления: {data}")
        await call.answer("Ошибка обработки запроса")
        return
    
    page = int(data[1])
    user_id = int(data[2])
    card_id = int(data[3])
    
    card_dao = BaseDAO(Card, db_session)
    moder_dao = BaseDAO(OnModeration, db_session)
    
    moder_card = await moder_dao.get_one(OnModeration.id == card_id)
    if not moder_card:
        await call.answer(f"Неизвестная карта пользователя {user_id}, либо уже была удалена")
        return
    
    create_card = await card_dao.create({
        "user_id": moder_card.user_id,
        "name": moder_card.name,
        "description": moder_card.description,
        "price": moder_card.price,
    })
    if not create_card:
        logger.error(f"Карточка юзера {user_id} не была добавлена")
        return
    
    cus = await create_update_statistic(db_session, moder_card.user_id, True)
    if not cus:
        return
    
    await bot.send_message(
        moder_card.user_id,
        text=f"Ваша карточка {moder_card.name} была успешно добавлена администратором!"
    )
    
    delete = await moder_dao.delete(OnModeration.id == card_id)
    if not delete:
        logger.error(f"Карточка {card_id} на модерации не была удалена")
        return
    
    await call.answer("Успешно добавлено!")
    new_page = slice_page_num(page)
    result = await slider_pages("moder", new_page, db_session)
    
    if result and isinstance(result, tuple) and len(result) == 3:
        result_text, next_user_id, next_card_id = result
        
        if result_text and next_user_id and next_card_id:
            await call.message.edit_text(
                result_text, 
                reply_markup=moder_slider_bt(new_page, next_user_id, next_card_id)
                )
            return
    
    await call.message.edit_text(
        "Больше нет карточек, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )
      
@router.callback_query(F.data.startswith(ModerCard.delete))
async def delete_card(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # delete_card-{page}-{user_id}-{card_id}
    data = call.data.split("-")
    if len(data) < 4:
        logger.error(f"Неправильный размер данных для кнопки удаления: {data}")
        await call.answer("Ошибка обработки запроса")
        return
    
    page = int(data[1])
    user_id = int(data[2])
    card_id = int(data[3])
    
    moder_dao = BaseDAO(OnModeration, db_session)
    
    card = await moder_dao.get_one(OnModeration.id == card_id)
    if not card:
        await call.answer("Карточка не найдена или уже удалена")
        return
    
    delete = await moder_dao.delete(OnModeration.id == card_id)
    if not delete:
        logger.error(f"Не удалось удалить карточку пользователя {user_id}")
        return
    
    cus = await create_update_statistic(db_session, user_id, False)
    if not cus:
        return
    
    await bot.send_message(
        user_id,
        f"Увы, но ваша карточка {card.name} была удалена по решению администрации"
    )
    
    await call.answer("Успешно удалено!")
    new_page = slice_page_num(page)
    result = await slider_pages("moder", new_page, db_session)
    
    if result and isinstance(result, tuple) and len(result) == 3:
        result_text, next_user_id, next_card_id = result
        
        if result_text and next_user_id and next_card_id:
            await call.message.edit_text(
                result_text, 
                reply_markup=moder_slider_bt(new_page, next_user_id, next_card_id)
                )
            return
    
    await call.message.edit_text(
        "Больше нет карточек, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )
      
@router.callback_query(F.data.startswith(ModerCard.change))
async def change_card(call: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    # change_card-{page}-{user_id}-{card_id}
    await call.answer()
    data = call.data.split("-")
    if len(data) < 4:
        logger.error(f"Неправильный размер данных для кнопки изменения: {data}")
        await call.answer("Ошибка обработки запроса")
        return

    page = int(data[1])
    user_id = int(data[2])
    card_id = int(data[3])

    moder_dao = BaseDAO(OnModeration, db_session)
    
    card = await moder_dao.get_one(OnModeration.id == card_id)
    if not card:
        logger.error(f"Ненайдена карточка юзера {user_id}, пожалуйста перейдите в меню")
        return

    await call.message.answer(
        "Выберите параметр который хотите изменить:",
        reply_markup=change_card_bt()
    )
    await state.set_data({
        "page": page,
        "user_id": user_id,
        "card_id": card_id,
        "name": card.name,
        "description": card.description,
    })
    await state.set_state(ChangeCardState.change_)
        
        
@router.callback_query(F.data == AdminMenu.statistic)
async def statistic(call: CallbackQuery, db_session: AsyncSession):
    page = 1
    result_text = await slider_pages("statistic", page, db_session)
    if result_text:
        await call.message.edit_text(
            result_text, 
            reply_markup=statistic_slider_bt(page)
            )
        return
    await call.answer("Нет пользователей для статистики")
    
    
@router.callback_query(F.data == AdminMenu.applications)
async def applications(call: CallbackQuery, db_session: AsyncSession):
    page = 1
    result = await slider_pages("applications", page, db_session)
    
    if result and isinstance(result, tuple):
        result_text, user_id, id_card = result
        
        if result_text and user_id and id_card:
            await call.message.edit_text(
                result_text, 
                reply_markup=applications_slider_bt(page, user_id, id_card)
                )
            return
    await call.answer("Нет заявок")

@router.callback_query(F.data.startswith(ApplicationsUsers.payment_completed))
async def payment_completed(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # payment_completed-{page}-{user_id}-{id_card}
    data = call.data.split("-")
    if len(data) < 4:
        logger.error(f"Неправильный размер данных для кнопки оплаты: {data}")
        await call.answer("Ошибка обработки запроса")
        return
    
    page = int(data[1])
    user_id = int(data[2])
    id_card = int(data[3])
    
    applications_dao = BaseDAO(Applications, db_session)

    delete_application = await applications_dao.delete(
        and_(Applications.user_id == user_id, Applications.id == id_card)
        )
    if not delete_application:
        logger.error(f"Карточка юзера {user_id} не была удалена, либо была не найдена")
        await call.answer("Карточка не найдена")
        return
    
    await call.answer("Успешно!")
    await bot.send_message(
        user_id,
        "На ваш кошелек успешно переведены средства!\n"
        "Теперь можно пользоваться выводом снова"
    )
    
    new_page = slice_page_num(page)
    result = await slider_pages("applications", new_page, db_session)
    
    if result and isinstance(result, tuple) and len(result) == 3:
        result_text, next_user_id, next_id_card = result
        if result_text and next_user_id and next_id_card:
            await call.message.edit_text(
                result_text, 
                reply_markup=applications_slider_bt(new_page, next_user_id, next_id_card)
                )
            return
    
    await call.message.edit_text(
        "Больше нет заявок, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )

@router.callback_query(F.data == AdminMenu.back_admin_menu)
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await admin_menu(call, state)
    
