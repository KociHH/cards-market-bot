from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from bot.admin.db.models.admin import Applications, OnModeration, Statistics
from bot.card.db.models.card import Card
from bot.shared.crud.user import UserSliderCrudShared
import logging

logger = logging.getLogger(__name__)


class UserSliderCrud(UserSliderCrudShared):
    def __init__(
        self,
        page: int,
        db_session: AsyncSession
        ) -> None:
        super().__init__(page, db_session)
    
    async def moder_data(self):
        moder_dao = BaseDAO(OnModeration, self.db_session)
        
        moder_card = await moder_dao.get_all()
        if not moder_card:
            return None, None, None
        
        max_lines = 1
        start_idx, end_idx = self.slice_calc(max_lines)
        
        if start_idx >= len(moder_card):
            return None, None, None
        
        card = moder_card[start_idx]
        
        result_text = (
                f"Карточка юзера {card.user_id}\n"
                f"Название: {card.name}\n"
                f"Описание: {card.description}\n"
                f"Цена: {card.price}\n\n"
            )
        
        return result_text, card.user_id, card.id
        
    async def statistic_data(self, max_lines: int | None = None):
        if not max_lines:
            max_lines = 8
        statistic_dao = BaseDAO(Statistics, self.db_session)
    
        statistic = await statistic_dao.get_all()
        if not statistic:
            return None
        
        start_idx, end_idx = self.slice_calc(max_lines)
        
        result_statistic = statistic[start_idx:end_idx]
        if not result_statistic:
            return None
        
        result_text = []
        for stat in result_statistic:
            result_text.append(
                f"Статистика {stat.user_id}\n"
                f"Одобрено: {stat.approved}\n"
                f"Отклонено: {stat.rejected}\n\n"
            )
        
        return "".join(result_text)
    
    async def applications_data(self):
        applications_dao = BaseDAO(Applications, self.db_session)
        
        applications = await applications_dao.get_all()
        if not applications:
            return None, None, None

        max_lines = 1
        start_idx, end_idx = self.slice_calc(max_lines)
        
        if start_idx >= len(applications):
            return None, None, None
        
        application = applications[start_idx]
        
        result_text = (
            f"Заявка на вывод юзера {application.username if application.username else application.user_id}\n"
            f"Сумма: {application.sum_withdrow}\n"
            f"Адрес кошелька: {application.address}"
        )
        return result_text, application.user_id, application.id
    

async def create_update_statistic(db_session: AsyncSession, user_id: str | int, approved: bool) -> bool:
    statistic_dao = BaseDAO(Statistics, db_session)
    statistic_user = await statistic_dao.get_one(Statistics.user_id == user_id)
    
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
        update_statistic = await statistic_dao.update(
            Statistics.user_id == user_id,
            data_update
        )
        if not update_statistic:
            logger.error(f"Не получилось обновить статистику юзера {user_id}")
            return False
    else:
        create_statistic = await statistic_dao.create(data_create)
        if not create_statistic:
            logger.error(f"Не получилось создать статистику юзера {user_id}")
            return False
    return True