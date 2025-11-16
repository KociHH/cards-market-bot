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
from modules.card.services.slider.service import SliderService
from modules.card.services.withdraw.service import WithdrawService
from modules.card.services.pay.service import PayService

router = Router(name=__name__)
logger = logging.getLogger(__name__)

slider_service = SliderService()
withdraw_service = WithdrawService()
pay_service = PayService()

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
    result = await slider_service.get_page_data("look", 1, db_session)
    
    if result:
        result_look = await slider_service.look.handle_look(result, 1)
        if not result_look.is_error:
            await result_look.call_message_edit_text(call)
            return
            
    await call.answer("Нет карточек для просмотра")

@router.callback_query(F.data == MenuUser.withdraw)
async def withdraw(call: CallbackQuery, db_session: AsyncSession, state: FSMContext):
    await call.answer()
    user_id = call.from_user.id
    
    result_withdraw = await withdraw_service.withdraw.handle_withdraw(db_session, user_id)
    
    await result_withdraw.call_message_answer(call)
    
    if result_withdraw.is_error:
        await result_withdraw.call_answer(call)
        return

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
    
    result_pay_card = await pay_service.pay_card.handle_pay_card(call.data, db_session)
    
    await result_pay_card.call_answer(call)
    
    if result_pay_card.is_error:
        return
    
    card_id = result_pay_card.get_key_return_data("card_id")
    card = result_pay_card.get_key_return_data("card")
    
    if any([card_id is None, card is None]):
        logger.error(f"Ненайдены параметры: card_id={card_id}, card={card}")
        await call.answer("Ошибка")
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
        logger.error(f"Ошибка при создании инвойса для карточки {card_id}: {e}")
        await call.answer("Ошибка при создании платежа")
    
    