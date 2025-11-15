import logging
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.utils import markdown
from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.crud.utils import slider_pages, send_card_invoice
from modules.card.keyboards.inline.callback_data import MenuUser, PayCard
from modules.card.keyboards.reply.buttons import sum_withdrow
from modules.card.keyboards.reply.states import EnterCard, Withdraw
from modules.card.keyboards.inline.buttons import look_card_pay_bt, menu_user, back_menu_card_inline_bt, slider_look, withdraw_bt
from modules.card.crud.user import UserDBCrud
from modules.card.crud.card import CardDBCrud
from modules.shared.services.utils import parsing_callback_data

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
    user_db_crud = UserDBCrud(user_id, db_session)
    
    result_balance = await user_db_crud.get_user_balance_or_zero()
        
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
    user_db_crud = UserDBCrud(user_id, db_session)
    
    result_balance = await user_db_crud.get_user_balance_or_zero()
    if result_balance == 0:
        await call.answer("Ваш баланс равняется 0")
        return
    
    application_user = await user_db_crud.get_application_user()
    if application_user:
        await call.answer("У вас уже есть активная заявка")
        return
    
    await call.answer()
    await call.message.answer(
        text="Пожалуйста укажите сумму вывода, либо нажмите на кнопку, чтобы вывести всю сумму:",
        reply_markup=sum_withdrow(result_balance)
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
    result_params = parsing_callback_data(call.data, 3)
    if not result_params:
        await call.answer("Ошибка обработки запроса")
        return
    
    page = int(result_params[0])
    card_id = int(result_params[1])
    
    card_db_crud = CardDBCrud(card_id, db_session)
    
    card = await card_db_crud.get_card()
    if not card:
        logger.error(f"Ненайдена карточка под id: {card_id}")
        await call.answer("Карточка не найдена")
        return
    
    if not card.price or card.price <= 0:
        logger.error(f"Невалидная цена карточки {card_id}: {card.price}")
        await call.answer("Ошибка: невалидная цена карточки")
        return
    
    try:
        order_id = card_id
        await send_card_invoice(
            bot, 
            call.from_user.id, 
            order_id, 
            card.price, 
            card.name, 
            card.description, 
            card.user_id
            )
    except ValueError as e:
        logger.error(f"Ошибка при создании инвойса для карточки {card_id}: {e}")
        await call.answer("Ошибка при создании платежа. Проверьте цену карточки.")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании инвойса для карточки {card_id}: {e}")
        await call.answer("Произошла ошибка при создании платежа")
    
    