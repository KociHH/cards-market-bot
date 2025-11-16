from typing import Any
from aiogram.types import CallbackQuery, Message


class ResultValidation:
    def __init__(
        self, 
        text: str, 
        is_error: bool, 
        return_data: dict = {}, 
        reply_markup: Any | None = None,
        call_message_answer_return: bool = False,
        message_edit_text_return: bool = False,
        call_message_edit_text_return: bool = False
        ) -> None:
        self.text = text
        self.is_error = is_error
        self.return_data = return_data
        self.reply_markup = reply_markup
        self.call_message_answer_return = call_message_answer_return
        self.message_edit_text_return = message_edit_text_return
        self.call_message_edit_text_return = call_message_edit_text_return
        
    async def call_answer(self, call: CallbackQuery):
        await call.answer(self.text)
        
    async def call_message_answer(self, call: CallbackQuery):
        if self.call_message_answer_return:
            await call.message.answer(self.text, reply_markup=self.reply_markup)
        
    async def call_message_edit_text(self, call: CallbackQuery):
        if self.call_message_edit_text_return:
            await call.message.edit_text(self.text, reply_markup=self.reply_markup)
        
    async def message_answer(self, message: Message):
        await message.answer(self.text, reply_markup=self.reply_markup)
        
    async def message_edit_text(self, message: Message):
        await message.edit_text(self.text, reply_markup=self.reply_markup)
        
    def get_key_return_data(self, key: str):
        if not self.return_data:
            return None
        
        return self.return_data.get(key)