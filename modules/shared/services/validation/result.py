from typing import Any
from aiogram.types import CallbackQuery, Message


class ResultValidation:
    def __init__(
        self, 
        text: str, 
        is_error: bool, 
        return_data: dict = {}, 
        reply_markup: Any | None = None
        ) -> None:
        self.text = text
        self.is_error = is_error
        self.return_data = return_data
        self.reply_markup = reply_markup
        
    async def call_answer(self, call: CallbackQuery):
        await call.answer(self.text)
        
    async def message_answer(self, message: Message):
        await message.answer(self.text, reply_markup=self.reply_markup)
        
    def get_key_return_data(self, key: str):
        if not self.return_data:
            return None
        
        return self.return_data.get(key)