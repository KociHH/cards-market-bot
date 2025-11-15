from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from db.models.admin import Applications, Statistics, OnModeration
from db.models.card import Card
from db.models.user import Balance, User


logger = logging.getLogger(__name__)

class CreateDBCrudShared:
    def __init__(
        self, 
        db_session: AsyncSession
        ) -> None:
        self.db_session = db_session
        
        self.user_dao = BaseDAO(User, self.db_session)
        self.balance_dao = BaseDAO(Balance, self.db_session)
        self.applications_dao = BaseDAO(Applications, self.db_session) 
        self.card_dao = BaseDAO(Card, self.db_session)   
        self.statistic_dao = BaseDAO(Statistics, self.db_session)   
        self.moder_dao = BaseDAO(OnModeration, self.db_session)  
    
    async def create_card(
        self,
        user_id: str | int,
        name: str,
        description: str,
        price: str | int
        ):
        create = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "price": price,
        }
        try:
            card = await self.card_dao.create(create)
            return card
        except Exception as e:
            logger.error(f"Не создалась таблица с юзером {user_id}: {e}")
            return
        

        
