import logging
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils import markdown
from aiogram import Router
from kos_Htools import BaseDAO
from sqlalchemy import and_
from modules.admin.crud.card import CardDBCrud
from modules.admin.crud.create import CreateDBCrud
from modules.admin.crud.user import UserDBCrud
from modules.admin.keyboards.inline.callback_data import AdminMenu, ApplicationsUsers, ModerCard, Slider
from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.keyboards.inline.buttons import admin_menu_bt, applications_slider_bt, back_admin_menu_bt, moder_slider_bt, statistic_slider_bt
from modules.admin.crud.utils import slider_pages
from modules.admin.keyboards.reply.button_names import ChangeCard
from modules.admin.keyboards.reply.buttons import change_card_bt
from modules.admin.keyboards.reply.states import ChangeCardState
from modules.admin.services.moder_card.change import ChangeService
from modules.admin.services.moder_card.delete import DeleteService
from modules.admin.services.slider.service import SliderProvideHandler
from modules.admin.services.moder_card.add import AddService
from modules.shared.crud.utils import slice_page_num
from modules.shared.services.utils import parsing_callback_data
from modules.shared.services.validation.result import ResultValidation

router = Router(name=__name__)
logger = logging.getLogger(__name__)

slider_provide_handler = SliderProvideHandler()
add_service = AddService()
delete_service = DeleteService()
change_service = ChangeService()

@router.callback_query(F.data == AdminMenu.admin)
async def admin_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        text="Меню админа:",
        reply_markup=admin_menu_bt()
    )

@router.callback_query(F.data == AdminMenu.moder)
async def moder(call: CallbackQuery, db_session: AsyncSession):
    result = await slider_provide_handler.get_page_data("moder", 1, db_session)
    if result:
        handle_moder = await slider_provide_handler.moder_handler.handle(result, 1, call)
        if handle_moder:
            return
    await call.answer("Нет карточек для проверки")
      
@router.callback_query(F.data.startswith(ModerCard.add))
async def add_card(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # add_card-{page}-{user_id}-{card_id}
    result_add = await add_service.handle(db_session, call.data)
    
    await result_add.call_answer(call)
    
    if result_add.is_error:
        return
    
    page = result_add.get_key_return_data("page")
    chat_id = result_add.get_key_return_data("chat_id")
    name = result_add.get_key_return_data("name")
    
    if any([page is None, chat_id is None, name is None]):
        logger.error(f"Ненайдены параметры: page={page}, chat_id={chat_id}, name={name}")
        await call.answer("Ошибка")
        return
    
    await bot.send_message(
        chat_id,
        text=f"Ваша карточка {name} была успешно добавлена администратором!"
    )
    
    new_page = slice_page_num(page)
    result = await slider_provide_handler.get_page_data("moder", new_page, db_session)
    
    if result:
        handler = slider_provide_handler.get_handler("moder")
        if handler:
            success = await handler.handle(result, new_page, call)
            if success:
                return
    
    await call.message.edit_text(
        "Больше нет карточек, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )
      
@router.callback_query(F.data.startswith(ModerCard.delete))
async def delete_card(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # delete_card-{page}-{user_id}-{card_id}
    result_delete = await delete_service.handle(call.data, db_session)
    
    await result_delete.call_answer(call)
    
    if result_delete.is_error:
        return
    
    page = result_delete.get_key_return_data("page")
    chat_id = result_delete.get_key_return_data("chat_id")
    name = result_delete.get_key_return_data("name")
    
    if any([page is None, chat_id is None, name is None]):
        logger.error(f"Ненайдены параметры: page={page}, chat_id={chat_id}, name={name}")
        await call.answer("Ошибка")
        return
    
    await bot.send_message(
        chat_id,
        f"Увы, но ваша карточка {name} была удалена по решению администрации"
    )
    
    new_page = slice_page_num(page)
    result = await slider_provide_handler.get_page_data("moder", new_page, db_session)
    
    if result:
        handle_moder = await slider_provide_handler.moder_handler.handle(result, new_page, call)
        if handle_moder:
            return
    
    await call.message.edit_text(
        "Больше нет карточек, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )
      
@router.callback_query(F.data.startswith(ModerCard.change))
async def change_card(call: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    # change_card-{page}-{user_id}-{card_id}
    await call.answer()
    result_change = await change_service.handle_change(call.data, db_session)

    if result_change.is_error:
        await result_change.call_answer(call)
        return

    page = result_change.get_key_return_data("page")
    user_id = result_change.get_key_return_data("user_id")
    name = result_change.get_key_return_data("name")
    card_id = result_change.get_key_return_data("card_id")
    description = result_change.get_key_return_data("description")
    
    if any([page is None, user_id is None, name is None, card_id is None, description is None]):
        logger.error(f"Ненайдены параметры: page={page}, user_id={user_id}, name={name}, card_id={card_id}, description={description}")
        await call.answer("Ошибка")
        return

    await call.message.answer(
        "Выберите параметр который хотите изменить:",
        reply_markup=change_card_bt()
    )
    await state.set_data({
        "page": page,
        "user_id": user_id,
        "card_id": card_id,
        "name": name,
        "description": description,
    })
    await state.set_state(ChangeCardState.change_)
        
        
@router.callback_query(F.data == AdminMenu.statistic)
async def statistic(call: CallbackQuery, db_session: AsyncSession):
    result = await slider_provide_handler.get_page_data("statistic", 1, db_session)
    if result:
        handle_stat = await slider_provide_handler.statistic_handler.handle(result, 1, call)
        if handle_stat:
            return
    await call.answer("Нет пользователей для статистики")
    
@router.callback_query(F.data == AdminMenu.applications)
async def applications(call: CallbackQuery, db_session: AsyncSession):
    result = await slider_provide_handler.get_page_data("applications", 1, db_session)
    if result:
        handle_stat = await slider_provide_handler.applications_handler.handle(result, 1, call)
        if handle_stat:
            return
    await call.answer("Нет заявок")

@router.callback_query(F.data.startswith(ApplicationsUsers.payment_completed))
async def payment_completed(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # payment_completed-{page}-{user_id}-{id_card}
    result_params = parsing_callback_data(call.data, 4)
    
    page = int(result_params[0])
    user_id = int(result_params[1])
    id_appl = int(result_params[2])
    
    user_db_crud = UserDBCrud(user_id, db_session)

    delete_application = await user_db_crud.delete_user_application(id_appl)
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
    result = await slider_provide_handler.get_page_data("applications", new_page, db_session)
    if result:
        handle_stat = await slider_provide_handler.applications_handler.handle(result, 1, call)
        if handle_stat:
            return
    
    await call.message.edit_text(
        "Больше нет заявок, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )

@router.callback_query(F.data == AdminMenu.back_admin_menu)
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await admin_menu(call, state)
    
