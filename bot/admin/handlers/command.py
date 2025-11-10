import logging
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command, StateFilter
from aiogram import Router
import asyncio
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from bot.admin.keyboards.reply.button_names import ChangeCard
from bot.admin.keyboards.reply.states import ChangeCardState
from bot.admin.db.models.admin import OnModeration
from bot.shared.db.models.user import User
from config import is_admin

router = Router(name=__name__)
logger = logging.getLogger(__name__)
