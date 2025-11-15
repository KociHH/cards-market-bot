import logging
from sqlalchemy.ext.asyncio import AsyncSession
from modules.admin.crud.card import CardDBCrud
from modules.admin.keyboards.inline.buttons import back_admin_menu_bt
from modules.admin.keyboards.reply.states import ChangeCardState
from modules.shared.services.utils import parsing_callback_data
from modules.shared.services.validation.result import ResultValidation


logger = logging.getLogger(__name__)

class ChangeService:
    def __init__(self) -> None:
        pass
    
    async def handle_change(
        self,
        calldata: str,
        db_session: AsyncSession
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
            logger.error(f"Ненайдена карточка юзера {user_id}")
            return ResultValidation(f"Ненайдена карточка юзера {user_id}, пожалуйста перейдите в меню", True)
        
        return ResultValidation(f"success", False, {
            "page": page,
            "user_id": user_id,
            "card_id": card_id,
            "name": card.name,
            "description": card.description
        })
    
    async def handle_name_description(
        self,
        db_session: AsyncSession,
        card_id: int | str,
        operation_name: str,
        text: str
        ) -> ResultValidation:
        card_db_crud = CardDBCrud(card_id, db_session)
    
        if operation_name == ChangeCardState.name:
            update_result = await card_db_crud.update_moder_card({"name": text})
            if not update_result:
                logger.error(f"Не получилось обновить название карточки {card_id}")
                return ResultValidation("Ошибка при обновлении названия", True)
        
            return ResultValidation(
                f"Успешно было изменено название на '{text}'! Продолжайте изменять, либо вернитесь обратно в меню", 
                False,
                {},
                back_admin_menu_bt()
            )
        
        elif operation_name == ChangeCardState.description:
            update_result = await card_db_crud.update_moder_card({"description": text})
            if not update_result:
                logger.error(f"Не получилось обновить описание карточки {card_id}")
                return ResultValidation("Ошибка при обновлении описания", True)
        
            return ResultValidation(
                f"Успешно было изменено описание на '{text}'! Продолжайте изменять, либо вернитесь обратно в меню", 
                False,
                {},
                back_admin_menu_bt()
            )
            
        logger.error(f"Неизвестное название operation_name: {operation_name}")
        return ResultValidation("Ошибка", True)