from datetime import datetime
from enum import StrEnum, auto
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import markdown
from modules.card.keyboards.inline.callback_data import MenuUser, PayCard
from modules.admin.keyboards.inline.callback_data import AdminMenu
from modules.shared.keyboards.inline import sliders_bt
from config import is_admin

def menu_user(user_id: str | int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Добавить карточку",
        callback_data=MenuUser.add_card
    )
    builder.button(
        text="Посмотреть карточки",
        callback_data=MenuUser.look_cards
    )
    builder.button(
        text="Баланс",
        callback_data=MenuUser.balance
    )
    if is_admin(user_id):
        builder.button(
            text="Меню админа",
            callback_data=AdminMenu.admin
        )
    builder.adjust(1)
    return builder.as_markup()

def back_menu_card_inline_bt(builder: InlineKeyboardBuilder | None = None) -> InlineKeyboardMarkup | InlineKeyboardBuilder:
    if not builder:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Вернуться в меню",
            callback_data=MenuUser.back_card_menu
        )
        builder.adjust(1)
        return builder.as_markup()
    else:
        builder.button(
            text="Вернуться в меню",
            callback_data=MenuUser.back_card_menu
        )
        return builder

def withdraw_bt() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Вывести",
        callback_data=MenuUser.withdraw,
    )
    back_menu_card_inline_bt(builder)
    builder.adjust(1)
    return builder.as_markup()

def look_card_bt(builder: InlineKeyboardBuilder, card_id: int, page: int) -> InlineKeyboardBuilder:
    builder.button(
        text="Купить",
        callback_data=f"{PayCard.pay}" + f"{page}-" + f"{card_id}"
    )
    return builder
   
def look_card_pay_bt() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Купить",
        pay=True
    )
    builder.adjust(1)
    return builder.as_markup()
    
def slider_look(page: int, card_id: int):
    builder = InlineKeyboardBuilder()
    
    sliders_bt(page, "look", builder)
    look_card_bt(builder, card_id, page)
    back_menu_card_inline_bt(builder)
    
    builder.adjust(2, 1)
    return builder.as_markup()