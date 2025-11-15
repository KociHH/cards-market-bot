from datetime import datetime
from enum import StrEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import markdown
from modules.card.keyboards.inline.callback_data import MenuUser
from modules.admin.keyboards.inline.callback_data import AdminMenu, Slider
from config import is_admin
from modules.shared.variables import type_admin_func, type_card_func
import logging

logger = logging.getLogger(__name__)

def sliders_bt(page: int, type_func: str, builder: InlineKeyboardBuilder | None = None) -> InlineKeyboardMarkup | InlineKeyboardBuilder:
    all_types = type_admin_func + type_card_func
    if type_func not in all_types:
        logger.error(f"Неправильный тип функции в sliders_bt: {type_func}") 
        return None
       
    if not builder:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="«",
            callback_data=Slider.slider_page + f"{page - 1}-" + type_func
        )
        builder.button(
            text="»",
            callback_data=Slider.slider_page + f"{page + 1}-" + type_func
        )
        builder.adjust(2, 1)
        return builder.as_markup()
    else:
        builder.button(
            text="«",
            callback_data=Slider.slider_page + f"{page - 1}-" + type_func
        )
        builder.button(
            text="»",
            callback_data=Slider.slider_page + f"{page + 1}-" + type_func
        )
        return builder