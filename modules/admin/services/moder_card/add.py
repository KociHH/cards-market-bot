import logging
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from modules.admin.crud.card import CardDBCrud
from modules.admin.crud.create import CreateDBCrud
from modules.shared.services.utils import parsing_callback_data
from modules.shared.services.validation.result import ResultValidation

logger = logging.getLogger(__name__)


class AddService:
    def __init__(self):
        pass

    async def handle(
        self,
        db_session: AsyncSession,
        calldata: str
    ) -> ResultValidation:
        result_params = parsing_callback_data(calldata, 4)
        if not result_params:
            logger.error(f"Неправильный размер данных для кнопки добавления: {calldata}")
            return ResultValidation("Ошибка обработки запроса", True)
    
        try:
            page = int(result_params[0])
            user_id = int(result_params[1])
            card_id = int(result_params[2])
        except (ValueError, IndexError):
            logger.error(f"Ошибка парсинга параметров: {calldata}")
            return ResultValidation("Ошибка обработки запроса", True)
        
        card_crud = CardDBCrud(card_id, db_session)
        moder_card = await card_crud.get_moder_card()
        if not moder_card:
            return ResultValidation(f"Неизвестная карта пользователя {user_id}, либо уже была удалена", True)
        
        created_card = await card_crud.create_card(
            user_id=moder_card.user_id,
            name=moder_card.name,
            description=moder_card.description,
            price=moder_card.price,
        )
        if not created_card:
            return ResultValidation("Ошибка", True)
        
        create_crud = CreateDBCrud(db_session)
        
        stat_result = await create_crud.create_update_statistic(moder_card.user_id, True)
        if not stat_result:
            return ResultValidation("Ошибка", True)
        
        deleted = await card_crud.delete_moder_card()
        if not deleted:
            logger.error(f"Карточка {card_id} на модерации не была удалена")
            return ResultValidation("Ошибка", True)
                
        return ResultValidation("Успешно добавлена!", False, {
            "page": page,
            "chat_id": moder_card.user_id,
            "name": moder_card.name
            })
