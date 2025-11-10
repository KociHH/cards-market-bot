import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
import asyncio

from kos_Htools import BaseDAO
from sqlalchemy import and_
from bot.card.keyboards.reply.button_names import AddCard
from sqlalchemy.ext.asyncio import AsyncSession
from bot.card.keyboards.reply.states import EnterCard, Withdraw
from bot.card.handlers.command import start_handler
from bot.card.db.models.card import Card
from bot.admin.db.models.admin import Applications, OnModeration
from bot.card.keyboards.reply.reply import back_menu_card_bt, send_on_admin_bt
from bot.card.keyboards.inline.inline import menu_user, back_menu_card_inline_bt
from bot.shared.db.models.user import Balance

router = Router(name=__name__)
logger = logging.getLogger(__name__)

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
    
    name = None
    price = None
    description = None
    
    lines = user_text.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("name-"):
            name = line.split("-", 1)[1].strip()
        elif line.startswith("price-"):
            price = line.split("-", 1)[1].strip()
        elif line.startswith("description-"):
            description = line.split("-", 1)[1].strip()
    
    if not name or not price or not description:
        await message.answer("Вы ввели не все обязательные параметры! Попробуйте еще раз")
        return
    
    try:
        price = int(price)
    except ValueError:
        await message.answer("Введите пожалуйста корректное число цены")
        return
    
    card_dao = BaseDAO(Card, db_session)
    moder_dao = BaseDAO(OnModeration, db_session)
    
    if_indices_card = await card_dao.get_one(and_(
        Card.name == name, Card.user_id == user_id, Card.description == description
    ))
    if_indices_moder = await moder_dao.get_one(and_(
        OnModeration.name == name, OnModeration.user_id == user_id, OnModeration.description == description
    ))
    
    if if_indices_card or if_indices_moder:
        await message.answer("У вас уже существует или уже расматривается индетичная карточка, пожалуйста измените параметры которую хотите добавить")
        return
    
    await message.answer(
        text="Отправить на рассмотрение администрации? Если нет, то продолжайте изменять параметры карточки",
        reply_markup=send_on_admin_bt()
        )
    
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
    card_dao = BaseDAO(OnModeration, db_session)
    
    name = card_data.get("name")
    price = card_data.get("price")
    description = card_data.get("description")
    user_id = card_data.get("user_id")
    
    if not all([name, price, description, user_id]):
        logger.error(f"Не хватает нескольких параметров карточки в card_data: {card_data}")
        await message.answer("Ошибка: не все данные сохранены. Попробуйте создать карточку заново.")
        return
    
    create = await card_dao.create({
        "name": name,
        "price": price,
        "description": description,
        "user_id": user_id
    })
    if not create:
        logger.error("Не создалась карточка товара для добавления в бд на проверку")
        return 
    
    await state.clear()
    await message.answer(
        "Карточка товара успешно добавлена на проверку администрации!\n"
        "Когда решит администрация добавить карту с изменениями или без, то мы вам сообщим.\n",
        reply_markup=back_menu_card_inline_bt()
        ) 
    
@router.message(StateFilter(EnterCard.send_on_admin))
async def change_card(message: Message, db_session: AsyncSession, state: FSMContext):
    await state.clear()
    await state.set_state(EnterCard.enter_card)
    await enter_card(message, db_session, state)
    
@router.message(StateFilter(Withdraw.sum_withdraw))
async def sum_withdraw(message: Message, state: FSMContext, db_session: AsyncSession):
    sum_w = message.text
    user_id = message.from_user.id
    balance_dao = BaseDAO(Balance, db_session)
    
    if not sum_w.isdigit():
        await message.answer(
            "Пожалуйста, введите число",
            reply_markup=back_menu_card_bt()
            )
        return
    
    balance_user = await balance_dao.get_one(Balance.user_id == user_id)
    if not balance_user or balance_user.balance == 0:
        await message.answer(
            "У вас баланс равняется 0, пожалуйста перейдите в меню",
            reply_markup=back_menu_card_bt()
            )
        await state.clear()
        return
    if balance_user.balance > int(sum_w):
        await message.answer(
            f"Извините, но введенная сумма {sum_w} больше, чем у вас есть {balance_user.balance}, повторите попытку еще раз",
            reply_markup=back_menu_card_bt()
            )
        return
    
    await state.set_data({
        "sum_withdrow": sum_w
    })
    await message.answer(
        "Теперь введите ваш полный адрес криптокошелька:",
        reply_markup=back_menu_card_bt()
        )
    
    await state.set_state(Withdraw.enter_address)
    
@router.message(StateFilter(Withdraw.enter_address))
async def enter_address(message: Message, db_session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    address = message.text
    if len(address) < 20:
        await message.answer(
            "Неккоректный размер адреса (допустимо от 20 символов)",
            reply_markup=back_menu_card_bt()
            )
        return
    
    data = await state.get_data()
    sum_withdrow = data.get("sum_withdrow")
    if not sum_withdrow:
        logger.error(f"Не хватает параметра sum_withdrow в дате состоянии: {data}")
    sum_withdrow = int(sum_withdrow)
    
    applications_dao = BaseDAO(Applications, db_session)
    
    create = await applications_dao.create({
        "user_id": user_id,
        "username": username,
        "address": address,
        "sum_withdrow": sum_withdrow
    })
    if not create:
        logger.error(f"Не создалась заявка на вывод пользователя {user_id}")
        return
    
    balance_dao = BaseDAO(Balance, db_session)
    
    balance_user = await balance_dao.get_one(Balance.user_id == user_id)
    if not balance_user:
        logger.error(f"Баланс пользователя {user_id} не найден")
        return
    
    balance_update = await balance_dao.update(
        Balance.user_id == user_id,
        {
            "balance": balance_user.balance - sum_withdrow
        }
    )
    if not balance_update:
        logger.error(f"Баланс пользователя {user_id} не был обновлен")
        return
    
    await message.answer(
        text=
        "Успешно! Ваша заявка на вывод была добавлена, после того как администраторы отправят вам деньги, мы вам сообщим!\n"
        "Пока ваша заявка расматривается, вам нельзя делать вывод средств",
        reply_markup=back_menu_card_bt()
        )
    await state.clear()
    