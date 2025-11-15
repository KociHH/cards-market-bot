import logging

from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.crud.slider import UserSliderCrud
from modules.shared.variables import type_admin_func

logger = logging.getLogger(__name__)

async def slider_pages(type_func: str, page: int, db_session: AsyncSession) -> str | None | tuple:
    if type_func not in type_admin_func:
        logger.error(f"Неправильный тип функции в slider_pages: {type_func}") 
        return None
    
    user_slider_crud = UserSliderCrud(page, db_session)
    
    if type_func == "statistic":
        return await user_slider_crud.statistic_data()
    elif type_func == "applications":
        return await user_slider_crud.applications_data()
    elif type_func == "moder":
        return await user_slider_crud.moder_data()
