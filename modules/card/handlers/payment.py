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

router = Router(name=__name__)
logger = logging.getLogger(__name__)

@router.pre_checkout_query()
async def on_pre_checkout(pre: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre.id, ok=True)

@router.message(F.successful_payment)
async def on_successful_payment(message: Message, db_session: AsyncSession):
    sp = message.successful_payment
    card_id = int(sp.invoice_payload)
    total = sp.total_amount / 100
    user_id = message.from_user.id
    
    create_db_crud = CreateDBCrud(db_session)
    card_db_crud = CardDBCrud(card_id, db_session)
    
    card_user = await card_db_crud.get_card()
    if not card_user:
        logger.error(f"Не найдена карточка {card_id}")
        await message.answer("Ошибка")
        return
    
    result_balance = await create_db_crud.create_update_balance(user_id, total)
    if not result_balance:
        await message.answer("Ошибка")
        return
    
    delete = await card_db_crud.delete_card()
    if not delete:
        logger.error(f"Не получилось удалить карточку пользователя {card_user.user_id}")
        await message.answer("Ошибка")
        return
    
    await message.answer(
        "Оплата успешно принята!",
        reply_markup=back_menu_card_inline_bt()
        )
    
    logger.info(f"Оплата прошла: {total} {sp.currency}, {card_id}")