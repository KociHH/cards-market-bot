import logging
from typing import Any
from aiogram.types import CallbackQuery
from modules.admin.keyboards.inline.buttons import moder_slider_bt, applications_slider_bt, statistic_slider_bt

logger = logging.getLogger(__name__)


class ModerHandler:
    async def handle(self, result: Any, page: int, call: CallbackQuery) -> bool:
        if isinstance(result, tuple) and len(result) == 3:
            result_text, user_id, card_id = result
            
            if result_text and user_id and card_id:
                await call.message.edit_text(
                    text=result_text,
                    reply_markup=moder_slider_bt(page, user_id, card_id)
                )
                return True
        return False


class ApplicationsHandler:
    async def handle(self, result: Any, page: int, call: CallbackQuery) -> bool:
        if isinstance(result, tuple) and len(result) == 3:
            result_text, user_id, card_id = result
            
            if result_text and user_id and card_id:
                await call.message.edit_text(
                    text=result_text,
                    reply_markup=applications_slider_bt(page, user_id, card_id)
                )
                return True
        return False
    
class StatisticHandler:
    async def handle(self, result: Any, page: int, call: CallbackQuery) -> bool:
        if isinstance(result, str) and result:
            await call.message.edit_text(
                text=result,
                reply_markup=statistic_slider_bt(page)
            )
            return True
        return False