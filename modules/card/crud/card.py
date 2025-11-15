from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.card import Card
from db.models.user import Balance
from modules.shared.crud.card import CardBDCrudShared
from modules.shared.crud.user import UserBDCrudShared
import logging


logger = logging.getLogger(__name__)

class CardDBCrud(CardBDCrudShared):
    def __init__(
        self, 
        card_id: str | int,
        db_session: AsyncSession
        ) -> None:
            super().__init__(card_id, db_session)
    