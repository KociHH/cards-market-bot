import logging
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils import markdown
from aiogram import Router
from sqlalchemy import and_
from modules.admin.crud.user import UserDBCrud
from modules.admin.keyboards.inline.callback_data import AdminMenu, ApplicationsUsers, ModerCard, Slider
from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.keyboards.inline.buttons import admin_menu_bt, applications_slider_bt, back_admin_menu_bt, moder_slider_bt, statistic_slider_bt
from modules.admin.keyboards.reply.buttons import change_card_bt
from modules.admin.keyboards.reply.states import ChangeCardState
from modules.admin.services.moder_card.service import ModerCardService
from modules.admin.services.slider.service import SliderService
from modules.admin.services.payment.service import PaymentService
from modules.shared.crud.utils import slice_page_num
from modules.shared.services.utils import parsing_callback_data

router = Router(name=__name__)
logger = logging.getLogger(__name__)

slider_service = SliderService()
moder_card_service = ModerCardService()
payment_service = PaymentService()

@router.callback_query(F.data == AdminMenu.admin)
async def admin_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        text="Меню админа:",
        reply_markup=admin_menu_bt()
    )

@router.callback_query(F.data == AdminMenu.moder)
async def moder(call: CallbackQuery, db_session: AsyncSession):
    result = await slider_service.get_page_data("moder", 1, db_session)
    if result:
        result_moder = await slider_service.moder.handle_moder(result, 1)
        if not result_moder.is_error:
            await result_moder.call_message_edit_text(call)
            return
        
    await call.answer("Нет карточек для проверки")
      
@router.callback_query(F.data.startswith(ModerCard.add))
async def add_card(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # add_card-{page}-{user_id}-{card_id}
    result_add = await moder_card_service.add.handle(db_session, call.data)
    
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
    result = await slider_service.get_page_data("moder", new_page, db_session)
    
    if result:
        result_moder = await slider_service.moder.handle_moder(result, new_page)
        if not result_moder.is_error:
            await result_moder.call_message_edit_text(call)
            return
    
    await call.message.edit_text(
        "Больше нет карточек, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )
      
@router.callback_query(F.data.startswith(ModerCard.delete))
async def delete_card(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # delete_card-{page}-{user_id}-{card_id}
    result_delete = await moder_card_service.delete.handle(call.data, db_session)
    
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
    result = await slider_service.get_page_data("moder", new_page, db_session)
    
    if result:
        result_moder = await slider_service.moder.handle_moder(result, new_page)
        if not result_moder.is_error:
            await result_moder.call_message_edit_text(call)
            return
    
    await call.message.edit_text(
        "Больше нет карточек, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )
      
@router.callback_query(F.data.startswith(ModerCard.change))
async def change_card(call: CallbackQuery, state: FSMContext, db_session: AsyncSession):
    # change_card-{page}-{user_id}-{card_id}
    await call.answer()
    result_change = await moder_card_service.change.handle_change(call.data, db_session)

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
    result = await slider_service.get_page_data("statistic", 1, db_session)
    if result:
        result_stat = await slider_service.statistic.handle_statistic(result, 1)
        if not result_stat.is_error:
            await result_stat.call_message_edit_text(call)
            return
        
    await call.answer("Нет пользователей для статистики")
    
@router.callback_query(F.data == AdminMenu.applications)
async def applications(call: CallbackQuery, db_session: AsyncSession):
    result = await slider_service.get_page_data("applications", 1, db_session)
    if result:
        result_appl = await slider_service.applications.handle_applications(result, 1)
        if not result_appl.is_error:
            await result_appl.call_message_edit_text(call)
            return
        
    await call.answer("Нет заявок")

@router.callback_query(F.data.startswith(ApplicationsUsers.payment_completed))
async def payment_completed(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # payment_completed-{page}-{user_id}-{id_card}
    
    result_payment = await payment_service.payment_completed.handle_payment_completed(db_session, call.data)
    
    await result_payment.call_answer(call)
    
    if result_payment.is_error:
        return
    
    user_id = result_payment.get_key_return_data("user_id")
    page = result_payment.get_key_return_data("page")
    
    if any([page is None, user_id is None]):
        logger.error(f"Ненайдены параметры: page={page}, user_id={user_id}")
        await call.answer("Ошибка")
        return
    
    await bot.send_message(
        user_id,
        "На ваш кошелек успешно переведены средства!\n"
        "Теперь можно пользоваться выводом снова"
    )
    
    new_page = slice_page_num(page)
    result = await slider_service.get_page_data("applications", new_page, db_session)
    if result:
        result_appl = await slider_service.applications.handle_applications(result, 1)
        if not result_appl.is_error:
            await result_appl.call_message_edit_text(call)
            return
    
    await call.message.edit_text(
        "Больше нет заявок, переходите в меню",
        reply_markup=back_admin_menu_bt()
        )

@router.callback_query(F.data == AdminMenu.back_admin_menu)
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await admin_menu(call, state)
    
