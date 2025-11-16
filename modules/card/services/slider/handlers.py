import logging
from typing import Any
from aiogram.types import CallbackQuery
from modules.card.keyboards.inline.buttons import slider_look
from modules.shared.services.validation.result import ResultValidation

logger = logging.getLogger(__name__)


class Look:  
    def __init__(self) -> None:
        pass
      
    async def handle_look(self, result: Any, page: int) -> ResultValidation:
        if isinstance(result, tuple) and len(result) == 2:
            result_text, card_id = result
            
            if result_text and card_id:
                return ResultValidation(result_text, False, {}, slider_look(page, card_id), call_message_edit_text_return=True)
        return ResultValidation("", True)
    
    async def handle(self, result: Any, page: int) -> ResultValidation:
        return await self.handle_look(result, page)
    
