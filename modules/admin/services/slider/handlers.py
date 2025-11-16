import logging
from typing import Any
from aiogram.types import CallbackQuery
from modules.admin.keyboards.inline.buttons import moder_slider_bt, applications_slider_bt, statistic_slider_bt
from modules.shared.services.validation.result import ResultValidation

logger = logging.getLogger(__name__)


class Moder:
    def __init__(self) -> None:
        pass
    
    async def handle_moder(self, result: Any, page: int) -> ResultValidation:
        if isinstance(result, tuple) and len(result) == 3:
            result_text, user_id, card_id = result
            
            if result_text and user_id and card_id:
                return ResultValidation(result_text, False, {}, moder_slider_bt(page, user_id, card_id), call_message_edit_text_return=True)
        return ResultValidation("", True)
    
    async def handle(self, result: Any, page: int) -> ResultValidation:
        return await self.handle_moder(result, page)


class Applications:
    def __init__(self) -> None:
        pass
    
    async def handle_applications(self, result: Any, page: int) -> ResultValidation:
        if isinstance(result, tuple) and len(result) == 3:
            result_text, user_id, card_id = result
            
            if result_text and user_id and card_id:
                return ResultValidation(result_text, False, {}, applications_slider_bt(page, user_id, card_id), call_message_edit_text_return=True)
        return ResultValidation("", True)
    
    async def handle(self, result: Any, page: int) -> ResultValidation:
        return await self.handle_applications(result, page)
    
class Statistic:
    def __init__(self) -> None:
        pass
    
    async def handle_statistic(self, result: Any, page: int) -> ResultValidation:
        if isinstance(result, str) and result:
            return ResultValidation(result, False, {}, statistic_slider_bt(page), call_message_edit_text_return=True)
        return ResultValidation("", True)    
    async def handle(self, result: Any, page: int) -> ResultValidation:
        return await self.handle_statistic(result, page)
