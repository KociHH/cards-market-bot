import logging

from sqlalchemy.ext.asyncio import AsyncSession
from bot.admin.crud.user import UserSliderCrud
from bot.shared.varibles import type_admin_func

logger = logging.getLogger(__name__)

async def slider_pages(type_func: str, page: int, db_session: AsyncSession) -> str | None | tuple:
    if type_func not in type_admin_func:
        logger.error(f"Неправильный тип функции в slider_pages: {type_func}") 
        return None
    
    usc = UserSliderCrud(page, db_session)
    
    if type_func == "statistic":
        return await usc.statistic_data()
    elif type_func == "applications":
        return await usc.applications_data()
    elif type_func == "moder":
        return await usc.moder_data()
