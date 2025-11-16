import logging
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram import Router
from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.keyboards.inline.callback_data import Slider
from modules.shared.services.slider.service import SliderService
from modules.shared.services.utils import parsing_callback_data

router = Router(name=__name__)
logger = logging.getLogger(__name__)

_slider_service = SliderService()

@router.callback_query(F.data.startswith(Slider.slider_page))
async def slider_handler(call: CallbackQuery, db_session: AsyncSession):
    # slider_page-{page}-{type}
    result_params = parsing_callback_data(call.data, 3)
    if not result_params:
        await call.answer("Ошибка обработки запроса")
        return
    
    try:
        page = int(result_params[0])
    except (ValueError, IndexError):
        logger.error(f"Ошибка парсинга параметров: {result_params}")
        await call.answer("Ошибка")
        return
    
    type_func = result_params[1]
    
    result_slider = await _slider_service.process_slider(type_func, page, db_session)
    
    await result_slider.call_answer(call)
    
    if result_slider.is_error:
        return
    
    result = result_slider.get_key_return_data("result")
    handler = result_slider.get_key_return_data("handler")
    page = result_slider.get_key_return_data("page")
    
    if any([page is None, result is None, handler is None]):
        logger.error(f"Ненайдены параметры: page={page}, result={result}, handler={handler}")
        await call.answer("Ошибка")
        return
    
    result_handler = await handler.handle(result, page)
    
    if result_handler.is_error:
        await call.answer("Нет больше данных")
        return
    
    await result_handler.call_message_edit_text(call)