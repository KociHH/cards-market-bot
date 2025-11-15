from kos_Htools import BaseDAO
from kos_Htools.sql.sql_alchemy.dao import AsyncSession
from sqlalchemy import and_
from config import is_admin
from db.models.admin import Applications, OnModeration
from db.models.card import Card
from db.models.user import Balance, User
from modules.shared.crud.user import UserBDCrudShared
import logging

logger = logging.getLogger(__name__)


class UserDBCrud(UserBDCrudShared):
    def __init__(
        self, 
        user_id: str | int,
        db_session: AsyncSession
        ) -> None:
            super().__init__(user_id, db_session)
        
    async def update_create_user(self) -> bool:
        update_create_data = {
            "user_id": self.user_id,
            "admin": is_admin(self.user_id)
        }
    
        user = await self.user_dao.get_one(User.user_id == self.user_id)
    
        if user:
            update = await self.user_dao.update(
                User.user_id == self.user_id,
                update_create_data
                )
            if not update:
                logger.error(f"Не обновился пользователь: {self.user_id}")
                return False
        else:
            create = await self.user_dao.create(update_create_data)
            if not create:
                logger.error(f"Пользватель {self.user_id} не был добавлен в бд")
                return False
        return True
    
    async def get_user_balance_or_zero(self):
        balance_user = await self.balance_dao.get_one(Balance.user_id == self.user_id)
        if balance_user:
            result_balance = balance_user.balance
        else:
            result_balance = 0
        return result_balance
    
    async def get_card_moder(
        self,
        name: str,
        description: str,
        ):
        if_indices_card = await self.card_dao.get_one(and_(
            Card.name == name, Card.user_id == self.user_id, Card.description == description
        ))
        if_indices_moder = await self.card_dao.get_one(and_(
            OnModeration.name == name, OnModeration.user_id == self.user_id, OnModeration.description == description
        ))
        return if_indices_card, if_indices_moder
    
    async def subtract_balance(self, withdrow: int):
        get_balance = await self.get_user_balance_or_zero()
        if not get_balance:
            logger.error(f"Ненайден баланс юзера {self.user_id}")
            return False
        
        balance = await self.balance_dao.update(
            Balance.user_id == self.user_id,
            {
                "balance": get_balance.balance - withdrow
            }
        )
        return balance
    