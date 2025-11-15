from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.crud.utils import slider_pages
from modules.admin.services.slider.handlers import ModerHandler, ApplicationsHandler, StatisticHandler


class SliderProvideHandler:
    def __init__(self) -> None:
        self.moder_handler = ModerHandler()
        self.applications_handler = ApplicationsHandler()
        self.statistic_handler = StatisticHandler()
    
        self.handlers = {
            "moder": self.moder_handler,
            "applications": self.applications_handler,
            "statistic": self.statistic_handler
        }
    
    async def get_page_data(self, type_func: str, page: int, db_session: AsyncSession):
        return await slider_pages(type_func, page, db_session)

    def get_handler(self, type_func: str):
        return self.handlers.get(type_func)