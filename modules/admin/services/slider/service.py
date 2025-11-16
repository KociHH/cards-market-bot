from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.crud.utils import slider_pages
from modules.admin.services.slider.handlers import Moder, Applications, Statistic


class SliderService:
    def __init__(self) -> None:
        self.moder = Moder()
        self.applications = Applications()
        self.statistic = Statistic()
    
        self.handlers = {
            "moder": self.moder,
            "applications": self.applications,
            "statistic": self.statistic
        }
    
    async def get_page_data(self, type_func: str, page: int, db_session: AsyncSession):
        return await slider_pages(type_func, page, db_session)

    def get_handler(self, type_func: str):
        return self.handlers.get(type_func)