from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.card import Card
from db.models.user import Balance
from modules.shared.crud.card import CardBDCrudShared
from db.models.admin import OnModeration
import logging
from typing import Any

logger = logging.getLogger(__name__)

class CardDBCrud(CardBDCrudShared):
    def __init__(
        self, 
        card_id: str | int,
        db_session: AsyncSession
        ) -> None:
            super().__init__(card_id, db_session)
            
    async def get_moder_card(self):
        moder_card = await self.moder_dao.get_one(OnModeration.id == self.card_id)
        return moder_card
    
    async def delete_moder_card(self):
        delete = await self.moder_dao.delete(OnModeration.id == self.card_id)
        return delete
    
    async def update_moder_card(self, data: dict[str: Any]):
        update = await self.moder_dao.update(
            OnModeration.id == self.card_id,
            data
        )
        return update