import logging
from sqlalchemy.ext.asyncio import AsyncSession
from modules.shared.services.validation.result import ResultValidation
from modules.shared.variables import type_admin_func, type_card_func
from modules.admin.services.slider.service import SliderProvideHandler as SliderProvideHandlerAdmin
from modules.card.services.slider.service import SliderProvideHandler as SliderProvideHandlerCard

logger = logging.getLogger(__name__)

class SliderService:    
    def __init__(self):
        self.admin_slider_provider = SliderProvideHandlerAdmin()
        self.card_slider_provider = SliderProvideHandlerCard()
    
    async def process_slider(
        self, 
        type_func: str, 
        page: int, 
        db_session: AsyncSession,
    ) -> ResultValidation:       
        if page < 1:
            return ResultValidation("Вы уже на первой странице", True)
        
        if type_func not in type_admin_func and type_func not in type_card_func:
            logger.error(f"Неправильный тип функции: {type_func}")
            return ResultValidation("Ошибка", True)
        
        if type_func in type_admin_func:
            provider = self.admin_slider_provider
        elif type_func in type_card_func:
            provider = self.card_slider_provider
        else:
            raise ValueError(f"Неизвестный тип функции: {type_func}")
        
        result = await provider.get_page_data(type_func, page, db_session)
        if not result:
            return ResultValidation("Нет больше данных", True)
            
        if isinstance(result, tuple):
            if any(item is None for item in result):
                return ResultValidation("Нет больше данных", True)
        
        handler = provider.get_handler(type_func)
        if not handler:
            logger.error(f"Обработчик для типа {type_func} не найден")
            return ResultValidation("Ошибка", True)
        
        return ResultValidation(
            "",
            False, 
            {
            "handler": handler,
            "page": page,
            "result": result
        })