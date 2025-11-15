from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from config import is_admin
from db.models.admin import Applications
from db.models.user import Balance, User
import logging
from modules.shared.crud.create import CreateDBCrudShared

logger = logging.getLogger(__name__)


class UserBDCrudShared(CreateDBCrudShared):
    def __init__(self, user_id: str | int, db_session: AsyncSession) -> None:
        super().__init__(db_session)
        self.user_id = user_id
        
    async def get_application_user(self):
        application_user = await self.applications_dao.get_one(Applications.user_id == self.user_id)
        return application_user
    
    async def get_balance_user(self):
        balance_user = await self.balance_dao.get_one(Balance.user_id == self.user_id)
        return balance_user