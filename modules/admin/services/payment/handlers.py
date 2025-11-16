from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.crud.user import UserDBCrud
import logging
from modules.shared.services.utils import parsing_callback_data
from modules.shared.services.validation.result import ResultValidation

logger = logging.getLogger(__name__)

class PaymentCompleted:
    def __init__(self):
        pass
    
    async def handle_payment_completed(
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
            id_appl = int(result_params[2])
        except (ValueError, IndexError):
            logger.error(f"Ошибка парсинга параметров: {calldata}")
            return ResultValidation("Ошибка обработки запроса", True)
    
        user_db_crud = UserDBCrud(user_id, db_session)

        delete_application = await user_db_crud.delete_user_application(id_appl)
        if not delete_application:
            logger.error(f"Карточка юзера {user_id} не была удалена, либо была не найдена")
            return ResultValidation("Карточка не найдена", True)
    
        return ResultValidation(
            "Успешно!", 
            False,
            {
                "user_id": user_id,
                "page": page
            }
            )