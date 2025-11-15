
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.card import Card
from modules.shared.crud.create import CreateDBCrudShared


class CardBDCrudShared(CreateDBCrudShared):
    def __init__(self, card_id: str | int, db_session: AsyncSession) -> None:
        super().__init__(db_session)
        self.card_id = card_id
        
    async def get_card(self):
        card = await self.card_dao.get_one(Card.id == self.card_id)
        return card
    
    async def delete_card(self):
        delete = await self.card_dao.delete(Card.id == self.card_id)
        return delete