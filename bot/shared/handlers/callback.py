import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
import asyncio
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from bot.admin.crud.utils import slider_pages as admin_slider_pages
from bot.card.crud.utils import slider_pages as card_slider_pages
from bot.admin.keyboards.inline.callback_data import Slider
from bot.card.keyboards.inline.callback_data import MenuUser
from bot.card.keyboards.reply.reply import sum_withdrow
from bot.card.keyboards.reply.states import EnterCard, Withdraw
from bot.card.keyboards.inline.inline import menu_user, back_menu_card_inline_bt, withdraw_bt
from bot.shared.db.models.user import Balance
from bot.shared.keyboard.inline import sliders_bt
from bot.shared.varibles import type_admin_func, type_card_func
from bot.admin.keyboards.inline.inline import applications_slider_bt, moder_slider_bt, statistic_slider_bt
from bot.card.keyboards.inline.inline import slider_look

router = Router(name=__name__)
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith(Slider.slider_page))
async def slider_handler(call: CallbackQuery, db_session: AsyncSession):
    # slider_page-{page}-{type}
    data = call.data.split("-")
    if len(data) < 3:
        logger.error(f"Неправильный формат callback_data: {call.data}")
        await call.answer("Ошибка обработки запроса")
        return
    
    page = int(data[1])
    type_func = data[2]
    
    if page < 1:
        await call.answer("Вы уже на первой странице")
        return
    
    if type_func not in type_admin_func and type_func not in type_card_func:
        logger.error(f"Неправильный тип функции: {type_func}")
        return
    
    slider_pages = card_slider_pages if type_func in type_card_func else admin_slider_pages
    
    valid_page = page
    result = await slider_pages(type_func, valid_page, db_session)
    
    if page == 0:
        await call.answer("Вы уже на первой странице")
        return
    
    if type_func in ["moder", "applications"]:
        if isinstance(result, tuple) and len(result) == 3:
            result_text, user_id, card_id = result
            if result_text and user_id and card_id:
                if type_func == "moder":
                    await call.message.edit_text(
                        text=result_text,
                        reply_markup=moder_slider_bt(valid_page, user_id, card_id)
                    )
                else:
                    await call.message.edit_text(
                        text=result_text,
                        reply_markup=applications_slider_bt(valid_page, user_id, card_id)
                    )
                return
    
    if type_func == "look":
        if isinstance(result, tuple) and len(result) == 2:
            result_text, card_id = result
            if result_text and card_id:
                await call.message.edit_text(
                    text=result_text,
                    reply_markup=slider_look(valid_page, card_id)
                )
                return
    
    if type_func == "statistic":
        if isinstance(result, str) and result:
            await call.message.edit_text(
                text=result,
                reply_markup=statistic_slider_bt(valid_page)
            )
            return
    
    await call.answer("Нет больше данных")