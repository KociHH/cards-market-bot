import logging
import uuid
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram import Router
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.crud.card import CardDBCrud
from modules.card.crud.create import CreateDBCrud
from modules.card.crud.user import UserDBCrud
from modules.card.keyboards.inline.buttons import back_menu_card_inline_bt
from modules.card.services.pay.service import PayService

router = Router(name=__name__)
logger = logging.getLogger(__name__)

pay_service = PayService()

@router.pre_checkout_query()
async def on_pre_checkout(pre: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre.id, ok=True)

@router.message(F.successful_payment)
async def on_successful_payment(message: Message, db_session: AsyncSession):
    sp = message.successful_payment
    card_id = int(sp.invoice_payload)
    total = sp.total_amount / 100
    user_id = message.from_user.id
    
    result_on_successful_payment = await pay_service.on_successful_payment.handle_on_successful_payment(db_session, card_id, user_id, total)
    
    await result_on_successful_payment.message_answer(message)
    
    if result_on_successful_payment.is_error:
        return
    
    logger.info(f"Оплата прошла: {total} {sp.currency}, {card_id}")