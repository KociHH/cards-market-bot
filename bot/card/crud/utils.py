import logging

from sqlalchemy.ext.asyncio import AsyncSession
from bot.card.crud.user import UserSliderCrud
from bot.shared.varibles import type_card_func

logger = logging.getLogger(__name__)

async def slider_pages(type_func: str, page: int, db_session: AsyncSession) -> str | None | tuple:
    if type_func not in type_card_func:
        logger.error(f"Неправильный тип функции в slider_pages: {type_func}") 
        return None
    
    usc = UserSliderCrud(page, db_session)
    
    if type_func == "look":
        return await usc.look_data()