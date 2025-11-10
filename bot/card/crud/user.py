from aiogram.types import LabeledPrice
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession

from bot.card.keyboards.inline.inline import look_card_pay_bt
from bot.admin.db.models.admin import Applications, OnModeration, Statistics
from bot.card.db.models.card import Card
from bot.shared.crud.user import UserSliderCrudShared
from config import YK_TEST_TOKEN
from aiogram import Bot

class UserSliderCrud(UserSliderCrudShared):
    def __init__(
        self,
        page: int,
        db_session: AsyncSession
        ) -> None:
        super().__init__(page, db_session)
        
    async def look_data(self):
        card_dao = BaseDAO(Card, self.db_session)
        
        cards = await card_dao.get_all()
        if not cards:
            return None, None

        max_lines = 1
        start_idx, end_idx = self.slice_calc(max_lines)
        
        if start_idx >= len(cards):
            return None, None
        
        card = cards[start_idx]
        
        result_text = (
            f"Карточка пользователя {card.user_id}\n"
            f"Название: {card.name}\n"
            f"Описание: {card.description}\n"
            f"Цена: {card.price}\n\n"
        )
        
        return result_text, card.id
    
async def send_card_invoice(
    bot: Bot, 
    chat_id: int, 
    order_id: str, 
    amount_rub: int, 
    title: str,
    description: str,
    user_id: str | int
    ):
    prices = [LabeledPrice(label=f"Карточка {user_id}", amount=amount_rub * 100)]
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