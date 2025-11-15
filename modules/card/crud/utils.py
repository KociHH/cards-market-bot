import logging

from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.crud.slider import UserSliderCrud
from modules.shared.variables import type_card_func
from aiogram.types import LabeledPrice
from modules.card.keyboards.inline.buttons import look_card_pay_bt
from config import YK_TEST_TOKEN
from aiogram import Bot


logger = logging.getLogger(__name__)

async def slider_pages(type_func: str, page: int, db_session: AsyncSession) -> str | None | tuple:
    if type_func not in type_card_func:
        logger.error(f"Неправильный тип функции в slider_pages: {type_func}") 
        return None
    
    usc = UserSliderCrud(page, db_session)
    
    if type_func == "look":
        return await usc.look_data()
    
async def send_card_invoice(
    bot: Bot, 
    chat_id: int, 
    order_id: str, 
    amount_rub: int, 
    title: str,
    description: str,
    user_id: str | int
    ):
    amount_rub *= 100
    prices = [LabeledPrice(label=f"Карточка {user_id}", amount=amount_rub)]
    await bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=f"{order_id}",
        currency="RUB",
        prices=prices,
        provider_token=YK_TEST_TOKEN,
        reply_markup=look_card_pay_bt()
    )