from sqlalchemy.ext.asyncio import AsyncSession
from db.models.user import Balance
from modules.shared.crud.create import CreateDBCrudShared
import logging


logger = logging.getLogger(__name__)

class CreateDBCrud(CreateDBCrudShared):
    def __init__(self, db_session: AsyncSession) -> None:
        super().__init__(db_session)
        
    async def create_update_balance(self, user_id: str | int, amount_whole: int):
        balance_user = await self.balance_dao.get_one(Balance.user_id == user_id)
        if balance_user:
            update = await self.balance_dao.update(
                Balance.user_id == user_id,
                {
                    "balance": balance_user.balance + amount_whole
                }
            )
            if not update:
                logger.error(f"Не получилось обновить баланс пользователя {user_id}")
                return False
        else:
            create = await self.balance_dao.create({
                "user_id": user_id,
                "balance": amount_whole
            })
            if not create:
                logger.error(f"Не получилось добавить пользователя {user_id}")
                return False
        return True
    
    async def create_applications(
        self,
        user_id: str | int,
        username: str,
        address: str,
        sum_withdrow: str | int
        ):
        try:
            create = await self.applications_dao.create({
                "user_id": user_id,
                "username": username,
                "address": address,
                "sum_withdrow": sum_withdrow
            })
            return create
        except Exception as e:
            logger.error(f"Не создалась заявка юзера {user_id}: {e}")
            return
        
    async def create_card_moder(
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
            card = await self.moder_dao.create(create)
            return card
        except Exception as e:
            logger.error(f"Не создалась таблица с юзером {user_id}: {e}")
            return