import logging
from modules.card.crud.card import CardDBCrud
from modules.shared.services.utils import parsing_callback_data
from modules.shared.services.validation.result import ResultValidation
from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.crud.create import CreateDBCrud
from modules.card.keyboards.inline.buttons import back_menu_card_inline_bt

logger = logging.getLogger(__name__)


class PayCard:
    def __init__(self):
        pass

    async def handle_pay_card(
        self,
        calldata: str,
        db_session: AsyncSession
        ) -> ResultValidation:
        result_params = parsing_callback_data(calldata, 3)
        if not result_params:
            return ResultValidation("Ошибка обработки запроса", True)
    
        try:
            page = int(result_params[0])
            card_id = int(result_params[1])
        except (ValueError, IndexError):
            logger.error(f"Ошибка парсинга параметров: {calldata}")
            return ResultValidation("Ошибка обработки запроса", True)
        
        card_db_crud = CardDBCrud(card_id, db_session)
    
        card = await card_db_crud.get_card()
        if not card:
            logger.error(f"Ненайдена карточка под id: {card_id}")
            return ResultValidation("Карточка не найдена", True)
        
        return ResultValidation(
            "", 
            False, 
            {
            "card_id": card_id,
            "card": card,
            })
        
class OnSuccessfulPayment:
    def __init__(self):
        pass
    
    async def handle_on_successful_payment(
        self,
        db_session: AsyncSession,
        card_id: str | int,
        user_id: str | int,
        total: int
    ) -> ResultValidation:
        create_db_crud = CreateDBCrud(db_session)
        card_db_crud = CardDBCrud(card_id, db_session)
    
        card_user = await card_db_crud.get_card()
        if not card_user:
            logger.error(f"Не найдена карточка {card_id}")
            return ResultValidation("Ошибка", True)
    
        result_balance = await create_db_crud.create_update_balance(user_id, total)
        if not result_balance:
            return ResultValidation("Ошибка", True)
    
        delete = await card_db_crud.delete_card()
        if not delete:
            logger.error(f"Не получилось удалить карточку пользователя {card_user.user_id}")
            return ResultValidation("Ошибка", True)
        
        return ResultValidation(
            "Оплата успешно принята!",
            False,
            reply_markup=back_menu_card_inline_bt()
            )
        