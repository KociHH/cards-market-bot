import logging
import uuid
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
import asyncio
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from bot.card.crud.user import send_card_invoice
from bot.card.crud.utils import slider_pages
from bot.card.keyboards.inline.callback_data import MenuUser, PayCard
from bot.card.keyboards.reply.reply import sum_withdrow
from bot.card.keyboards.reply.states import EnterCard, Withdraw
from bot.card.keyboards.inline.inline import look_card_pay_bt, menu_user, back_menu_card_inline_bt, slider_look, withdraw_bt
from bot.card.db.models.card import Card
from bot.admin.db.models.admin import Applications
from bot.shared.db.models.user import Balance

router = Router(name=__name__)
logger = logging.getLogger(__name__)

@router.callback_query(F.data == MenuUser.add_card)
async def add_card(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text=
        "Добавление карточки\n"
        "Пример добавления:\n\n"
        "name-Продажа ноутбука\n"
        "price-100\n"
        "description-Продаю ноутбук, принимаю trade in\n",
        reply_markup=back_menu_card_inline_bt()
    )
    await state.set_state(EnterCard.enter_card)
    
@router.callback_query(F.data == MenuUser.balance)
async def balance(call: CallbackQuery, db_session: AsyncSession):
    user_id = call.from_user.id
    balance_dao = BaseDAO(Balance, db_session)
    
    balance_user = await balance_dao.get_one(Balance.user_id == user_id)
    if balance_user:
        result_balance = balance_user.balance
    else:
        result_balance = 0
        
    await call.message.edit_text(
        text=
        f"Ваш баланс: {result_balance}",
        reply_markup=withdraw_bt()
    )

@router.callback_query(F.data == MenuUser.look_cards)
async def look_cards(call: CallbackQuery, db_session: AsyncSession):
    result = await slider_pages("look", 1, db_session)
    
    if result and isinstance(result, tuple):
        result_text, card_id = result
        
        if result_text and card_id:
            await call.message.edit_text(
                result_text, 
                reply_markup=slider_look(1, card_id)
                )
            return
    await call.answer("Нет карточек для просмотра")

@router.callback_query(F.data == MenuUser.withdraw)
async def withdraw(call: CallbackQuery, db_session: AsyncSession, state: FSMContext):
    user_id = call.from_user.id
    balance_dao = BaseDAO(Balance, db_session)
    
    balance_user = await balance_dao.get_one(Balance.user_id == user_id)
    if not balance_user:
        await call.answer("Ваш баланс равняется 0")
        return
    
    applications_dao = BaseDAO(Applications, db_session)
    
    application_user = await applications_dao.get_one(Applications.user_id == user_id)
    if application_user:
        await call.answer("У вас уже есть активная заявка")
        return
    
    await call.answer()
    await call.message.answer(
        text="Пожалуйста укажите сумму вывода, либо нажмите на кнопку, чтобы вывести всю сумму:",
        reply_markup=sum_withdrow(balance_user.balance)
        )
    await state.set_state(Withdraw.sum_withdraw)

@router.callback_query(F.data == MenuUser.back_card_menu)
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        text=
        f"Привет {call.from_user.full_name}!\n"
        "Меню:",
        reply_markup=menu_user(call.from_user.id)
    )
    
@router.callback_query(F.data.startswith(PayCard.pay))
async def pay_card(call: CallbackQuery, db_session: AsyncSession, bot: Bot):
    # pay_card-{page}-{card_id}
    await call.answer()
    data = call.data.split("-")
    if len(data) < 3:
        logger.error(f"Неправильный размер данных для кнопки покупаки карточки: {data}")
        await call.answer("Ошибка обработки запроса")
        return
    
    page = int(data[1])
    card_id = int(data[2])
    
    card_dao = BaseDAO(Card, db_session)
    
    card = await card_dao.get_one(Card.id == card_id)
    if not card:
        logger.error(f"Ненайдена карточка под id: {card_id}")
        await call.answer("Карточка не найдена")
        return
    
    order_id = card_id
    await send_card_invoice(bot, call.from_user.id, order_id, card.price, card.name, card.description, card.user_id)
    
    