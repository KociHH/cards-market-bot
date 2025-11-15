import logging
from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.crud.card import CardDBCrud
from modules.admin.crud.create import CreateDBCrud
from modules.shared.services.utils import parsing_callback_data
from modules.shared.services.validation.result import ResultValidation


logger = logging.getLogger(__name__)

class DeleteService:
    def __init__(self) -> None:
        pass
    
    async def handle(
        self, 
        calldata: str, 
        db_session: AsyncSession,
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
    
        card_db_crud = CardDBCrud(card_id, db_session)
        card = await card_db_crud.get_moder_card()
        if not card:
            return ResultValidation("Карточка не найдена или уже удалена", True)
    
        delete = await card_db_crud.delete_moder_card()
        if not delete:
            logger.error(f"Не удалось удалить карточку пользователя {user_id}")
            return ResultValidation("Ошибка", True)
    
        create_db_crud = CreateDBCrud(db_session)
    
        create_update_stat = await create_db_crud.create_update_statistic(user_id, False)
        if not create_update_stat:
            return ResultValidation("Ошибка при обновлении статистики", True)
    
        return ResultValidation("Успешно удалено!", False, {
            "page": page,
            "chat_id": user_id,
            "name": card.name
        })