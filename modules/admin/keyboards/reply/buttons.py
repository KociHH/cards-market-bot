from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from modules.admin.keyboards.reply.button_names import AdminMenu, ChangeCard

def change_card_bt():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=ChangeCard.name
    )
    builder.button(
        text=ChangeCard.description
    )
    back_menu_admin_reply_bt(builder)
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def back_menu_admin_reply_bt(builder: ReplyKeyboardBuilder | None = None) -> ReplyKeyboardMarkup | ReplyKeyboardBuilder:
    if not builder:
        builder = ReplyKeyboardBuilder()
        builder.button(
            text=AdminMenu.back_admin_menu,
        )
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
    else:
        builder.button(
            text=AdminMenu.back_admin_menu,
        )
        return builder