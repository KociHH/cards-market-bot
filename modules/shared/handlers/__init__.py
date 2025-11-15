__all__ = 'router'

from aiogram import Router
from modules.shared.handlers.callback import router as callback_router

router = Router(name=__name__)
router.include_router(callback_router)