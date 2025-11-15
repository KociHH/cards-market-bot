from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.admin import Applications, OnModeration, Statistics
from modules.shared.crud.slider import SliderCrudShared
import logging

logger = logging.getLogger(__name__)


class UserSliderCrud(SliderCrudShared):
    def __init__(
        self,
        page: int,
        db_session: AsyncSession
        ) -> None:
        super().__init__(page, db_session)
    
    async def moder_data(self):
        moder_card = await self.moder_dao.get_all()
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
        statistic = await self.statistic_dao.get_all()
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
        applications = await self.applications_dao.get_all()
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
    
