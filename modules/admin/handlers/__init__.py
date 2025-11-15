__all__ = 'router'

from aiogram import Router
from modules.admin.handlers.command import router as command_router
from modules.admin.handlers.callback import router as callback_router
from modules.admin.handlers.state import router as state_router

router = Router(name=__name__)
router.include_routers(command_router, callback_router, state_router)