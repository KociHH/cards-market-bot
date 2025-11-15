from re import S
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.admin import Applications, OnModeration, Statistics
import logging

from modules.shared.crud.create import CreateDBCrudShared

logger = logging.getLogger(__name__)


class SliderCrudShared(CreateDBCrudShared):
    def __init__(
        self,
        page: int,
        db_session: AsyncSession
        ) -> None:
        super().__init__(db_session)
        self.page = page
    
    def slice_calc(self, max_lines: int):
        """return: (start_idx, end_idx)"""
        start_idx = (self.page - 1) * max_lines
        end_idx = start_idx + max_lines
        return start_idx, end_idx
    