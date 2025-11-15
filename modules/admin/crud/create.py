from sqlalchemy.ext.asyncio import AsyncSession
import logging
from db.models.admin import Statistics
from modules.shared.crud.create import CreateDBCrudShared


logger = logging.getLogger(__name__)

class CreateDBCrud(CreateDBCrudShared):
    def __init__(self, db_session: AsyncSession) -> None:
        super().__init__(db_session)
        
    async def create_update_statistic(self, user_id: str | int, approved: bool) -> bool:
        try:
            statistic_user = await self.statistic_dao.get_one(Statistics.user_id == user_id)
    
            if approved:
                data_create = {
                    "user_id": user_id,
                    "approved": 1,
                    "rejected": 0,
                }
            else:
                data_create = {
                    "user_id": user_id,
                    "approved": 0,
                    "rejected": 1,
                }
    
            if statistic_user:
                if approved:
                    data_update = {
                        "approved": statistic_user.approved + 1
                    }
                else:
                    data_update = {
                        "rejected": statistic_user.rejected + 1
                    }
                update_statistic = await self.statistic_dao.update(
                    Statistics.user_id == user_id,
                    data_update
                )
                if not update_statistic:
                    logger.error(f"Не получилось обновить статистику юзера {user_id}")
                    return False
            else:
                create_statistic = await self.statistic_dao.create(data_create)
                if not create_statistic:
                    logger.error(f"Не получилось создать статистику юзера {user_id}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании или обновлении таблицы: {e}")
            return False