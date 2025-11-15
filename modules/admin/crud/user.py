from kos_Htools import BaseDAO
from kos_Htools.sql.sql_alchemy.dao import AsyncSession
from sqlalchemy import and_
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
            
    async def delete_user_application(self, id_appl: int | str):
        delete = await self.applications_dao.delete(
            and_(Applications.id == id_appl, Applications.user_id == self.user_id)
        )
        return delete