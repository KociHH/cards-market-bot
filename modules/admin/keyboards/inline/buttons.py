from datetime import datetime
from enum import StrEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import markdown
from modules.admin.keyboards.inline.callback_data import AdminMenu, ApplicationsUsers, ModerCard, Slider
from modules.shared.keyboards.inline import sliders_bt
from modules.card.keyboards.inline.buttons import back_menu_card_inline_bt
import logging


logger = logging.getLogger(__name__)

def admin_menu_bt() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Модерация",
        callback_data=AdminMenu.moder
    )
    builder.button(
        text="Статистика",
        callback_data=AdminMenu.statistic
    )
    builder.button(
        text="Заявки на вывод",
        callback_data=AdminMenu.applications
    )
    back_menu_card_inline_bt(builder)
    builder.adjust(1)
    return builder.as_markup()

def back_admin_menu_bt(builder: InlineKeyboardBuilder | None = None) -> InlineKeyboardMarkup | InlineKeyboardBuilder:
    if not builder:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Вернуться в меню",
            callback_data=AdminMenu.back_admin_menu
        )
        builder.adjust(1)
        return builder.as_markup()
    else:
        builder.button(
            text="Вернуться в меню",
            callback_data=AdminMenu.back_admin_menu
        )
        return builder
    
def moder_card_bt(builder: InlineKeyboardBuilder, user_id: str | int, card_id: str | int, page: int) -> InlineKeyboardBuilder:
    builder.button(
        text="Добавить",
        callback_data=ModerCard.add + f"{page}-{user_id}-{card_id}"
    )
    builder.button(
        text="Удалить",
        callback_data=ModerCard.delete + f"{page}-{user_id}-{card_id}"
    )
    builder.button(
        text="Изменить",
        callback_data=ModerCard.change + f"{page}-{user_id}-{card_id}"
    )
    return builder

def applications_bt(builder: InlineKeyboardBuilder, page: int, user_id: str | int, id_card: str | int) -> InlineKeyboardBuilder:
    builder.button(
        text="Оплата проведена",
        callback_data=ApplicationsUsers.payment_completed + f"{page}-" + f"{user_id}-" + f"{id_card}"
    )
    return builder


def moder_slider_bt(page: int, user_id: int | str, card_id: int | str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    sliders_bt(page, "moder", builder)
    moder_card_bt(builder, user_id, card_id, page)
    back_admin_menu_bt(builder)
    
    builder.adjust(2, 1)
    return builder.as_markup()
    
def applications_slider_bt(page: int, user_id: int | str, id_card: str | int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    sliders_bt(page, "applications", builder)
    applications_bt(builder, page, user_id, id_card)
    back_admin_menu_bt(builder)
    
    builder.adjust(2, 1)
    return builder.as_markup()

def statistic_slider_bt(page: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    sliders_bt(page, "statistic", builder)
    back_admin_menu_bt(builder)
    
    builder.adjust(2, 1)
    return builder.as_markup()