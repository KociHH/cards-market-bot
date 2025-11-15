import logging
from typing import Any
from aiogram.types import CallbackQuery
from modules.card.keyboards.inline.buttons import slider_look

logger = logging.getLogger(__name__)


class LookHandler:    
    async def handle(self, result: Any, page: int, call: CallbackQuery) -> bool:
        if isinstance(result, tuple) and len(result) == 2:
            result_text, card_id = result
            
            if result_text and card_id:
                await call.message.edit_text(
                    text=result_text,
                    reply_markup=slider_look(page, card_id)
                )
                return True
        return False
    