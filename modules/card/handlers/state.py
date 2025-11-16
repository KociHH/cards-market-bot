import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
from modules.card.crud.create import CreateDBCrud
from modules.card.crud.user import UserDBCrud
from modules.card.keyboards.reply.button_names import AddCard
from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.keyboards.reply.states import EnterCard, Withdraw
from modules.card.keyboards.reply.buttons import back_menu_card_bt, send_on_admin_bt
from modules.card.keyboards.inline.buttons import menu_user, back_menu_card_inline_bt
from modules.card.services.enter_card.service import EnterCardService
from modules.card.services.withdraw.service import WithdrawService


router = Router(name=__name__)
logger = logging.getLogger(__name__)

enter_card_service = EnterCardService()
withdraw_service = WithdrawService()

@router.message(F.text == AddCard.back_card_menu)
async def back_card_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    await message.answer(
        text=
        f"Привет {message.from_user.full_name}!\n"
        "Меню:",
        reply_markup=menu_user(user_id)
    )

@router.message(StateFilter(EnterCard.enter_card))
async def enter_card(message: Message, db_session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    user_text = message.text.strip()
    
    result_enter_card = await enter_card_service.enter_card.handle_enter_card(user_text, user_id, db_session)
    
    await result_enter_card.message_answer(message)
    
    if result_enter_card.is_error:
        return
    
    name = result_enter_card.get_key_return_data("name")
    price = result_enter_card.get_key_return_data("price")
    description = result_enter_card.get_key_return_data("description")
    user_id = result_enter_card.get_key_return_data("user_id")
    
    if any([name is None, price is None, description is None, user_id is None]):
        logger.error(f"Ненайдены параметры: name={name}, price={price}, description={description}, user_id={user_id}")
        await message.answer("Ошибка")
        return
    
    await state.set_state(EnterCard.send_on_admin)
    await state.set_data({
        "name": name,
        "price": price,
        "description": description,
        "user_id": user_id
    })
    
@router.message(F.text == AddCard.send_on_admin, StateFilter(EnterCard.send_on_admin))
async def send_on_admin(message: Message, db_session: AsyncSession, state: FSMContext):
    card_data = await state.get_data()
    
    result_send_on_admin = await enter_card_service.send_on_admin.handle_send_on_admin(db_session, card_data)
    
    await result_send_on_admin.message_answer(message)
    
    if result_send_on_admin.is_error:
        return
    
    await state.clear()
    
@router.message(StateFilter(EnterCard.send_on_admin))
async def change_card(message: Message, db_session: AsyncSession, state: FSMContext):
    await state.clear()
    await state.set_state(EnterCard.enter_card)
    await enter_card(message, db_session, state)
    
@router.message(StateFilter(Withdraw.sum_withdraw))
async def sum_withdraw(message: Message, state: FSMContext, db_session: AsyncSession):
    sum_w = message.text
    user_id = message.from_user.id
    
    result_sum_withdraw = await withdraw_service.sum_withdraw.handle_sum_withdraw(sum_w, db_session, user_id)
    
    await result_sum_withdraw.message_answer(message)

    if result_sum_withdraw.is_error:
        return
    
    await state.set_data({
        "sum_withdrow": sum_w
    })
    await state.set_state(Withdraw.enter_address)
    
@router.message(StateFilter(Withdraw.enter_address))
async def enter_address(message: Message, db_session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    address = message.text
    
    data = await state.get_data()
    
    result_sum_withdraw = await withdraw_service.enter_address.handle_enter_address(address, db_session, data, user_id, username)
    
    await result_sum_withdraw.message_answer(message)
    
    if result_sum_withdraw.is_error:
        return
    
    await state.clear()
    