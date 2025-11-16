from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.crud.utils import slider_pages
from modules.card.services.slider.handlers import Look


class SliderService:
    def __init__(self) -> None:
        self.look = Look()
        
        self.handlers = {
            "look": self.look
        }
    
    async def get_page_data(self, type_func: str, page: int, db_session: AsyncSession):
        return await slider_pages(type_func, page, db_session)
    
    def get_handler(self, type_func: str):
        return self.handlers.get(type_func)
