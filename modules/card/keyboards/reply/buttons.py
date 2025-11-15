from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from modules.card.keyboards.reply.button_names import AddCard

def send_on_admin_bt():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=AddCard.send_on_admin
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def sum_withdrow(sum: str | int):
    builder = ReplyKeyboardBuilder()
    builder.button(
        text=f"{sum}"
    )
    back_menu_card_bt(builder)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def back_menu_card_bt(builder: ReplyKeyboardBuilder | None = None) -> ReplyKeyboardMarkup | ReplyKeyboardBuilder:
    if not builder:
        builder = ReplyKeyboardBuilder()
        builder.button(
            text=AddCard.back_card_menu,
        )
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
    else:
        builder.button(
            text=AddCard.back_card_menu,
        )
        return builder