__all__ = 'router'

from aiogram import Router
from bot.card.handlers.command import router as command_router
from bot.card.handlers.callback import router as callback_router
from bot.card.handlers.state import router as state_router
from bot.card.handlers.payment import router as payment_router

router = Router(name=__name__)
router.include_routers(command_router, callback_router, state_router, payment_router)