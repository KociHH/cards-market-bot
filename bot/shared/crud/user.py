from re import S
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from bot.admin.db.models.admin import Applications, OnModeration, Statistics
from bot.card.db.models.card import Card

class UserSliderCrudShared:
    def __init__(
        self,
        page: int,
        db_session: AsyncSession
        ) -> None:
        self.page = page
        self.db_session = db_session
    
    def slice_calc(self, max_lines: int):
        """return: (start_idx, end_idx)"""
        start_idx = (self.page - 1) * max_lines
        end_idx = start_idx + max_lines
        return start_idx, end_idx
    