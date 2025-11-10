import logging
import uuid
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram import Router
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from bot.card.keyboards.inline.inline import back_menu_card_inline_bt
from bot.shared.db.models.user import Balance
from bot.card.db.models.card import Card

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
    
    balance_dao = BaseDAO(Balance, db_session)
    card_dao = BaseDAO(Card, db_session)
    
    card_user = await card_dao.get_one(Card.id == card_id)
    if not card_user:
        logger.error(f"Не найдена краточка пользователя {user_id}")
        return
    
    balance_user = await balance_dao.get_one(Balance.user_id == card_user.user_id)
    if balance_user:
        update = await balance_dao.update(
            Balance.user_id == card_user.user_id,
            {
                "balance": balance_user.balance + total
            }
        )
        if not update:
            logger.error(f"Не получилось обновить баланс пользователя {card_user.user_id}")
            return
    else:
        create = await balance_dao.create({
            "user_id": card_user.user_id,
            "balance": total
        })
        if not create:
            logger.error(f"Не получилось добавить пользователя {card_user.user_id}")
            return
    
    delete = await card_dao.delete(Card.id == card_id)
    if not delete:
        logger.error(f"Не получилось удалить карточку пользователя {card_user.user_id}")
        return
    
    await message.answer(
        "Оплата успешно принята!",
        reply_markup=back_menu_card_inline_bt()
        )
    
    logger.info(f"Оплата прошла: {total} {sp.currency}, {card_id}")