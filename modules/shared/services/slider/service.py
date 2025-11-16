import logging
from sqlalchemy.ext.asyncio import AsyncSession
from modules.shared.services.validation.result import ResultValidation
from modules.shared.variables import type_admin_func, type_card_func
from modules.admin.services.slider.service import SliderService as SliderServiceHandlerAdmin
from modules.card.services.slider.service import SliderService as SliderServiceHandlerCard

logger = logging.getLogger(__name__)

class SliderService:    
    def __init__(self):
        self.admin_slider_service = SliderServiceHandlerAdmin()
        self.card_slider_service = SliderServiceHandlerCard()
    
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
            service = self.admin_slider_service
        elif type_func in type_card_func:
            service = self.card_slider_service
        else:
            raise ValueError(f"Неизвестный тип функции: {type_func}")
        
        result = await service.get_page_data(type_func, page, db_session)
        if not result:
            return ResultValidation("Нет больше данных", True)
            
        if isinstance(result, tuple):
            if any(item is None for item in result):
                return ResultValidation("Нет больше данных", True)
        
        handler = service.get_handler(type_func)
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