from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from modules.shared.crud.slider import SliderCrudShared
import logging
from db.models.card import Card

class UserSliderCrud(SliderCrudShared):
    def __init__(
        self,
        page: int,
        db_session: AsyncSession
        ) -> None:
        super().__init__(page, db_session)
        
    async def look_data(self):
        cards = await self.card_dao.get_all()
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
    
