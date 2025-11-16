from modules.shared.services.validation.result import ResultValidation
import logging
from modules.card.crud.create import CreateDBCrud
from modules.card.crud.user import UserDBCrud
from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.keyboards.reply.buttons import back_menu_card_bt
from modules.card.keyboards.reply.buttons import sum_withdrow

logger = logging.getLogger(__name__)

class EnterAddress:
    def __init__(self):
        pass
    
    async def handle_enter_address(
        self,
        address: str,
        db_session: AsyncSession,
        data: dict,
        user_id: str | int,
        username: str | None,
    ) -> ResultValidation:
        if len(address) < 20:
            return ResultValidation(
                "Неккоректный размер адреса (допустимо от 20 символов)",
                True,
                reply_markup=back_menu_card_bt()
                ) 
    
        sum_withdrow = data.get("sum_withdrow")
        if not sum_withdrow:
            logger.error(f"Не хватает параметра sum_withdrow в дате состоянии: {data}")
            return ResultValidation("Ошибка", True)
        
        sum_withdrow = int(sum_withdrow)
    
        create_db_crud = CreateDBCrud(db_session)
    
        create = await create_db_crud.create_applications(
            user_id = user_id,
            username = username,
            address = address,
            sum_withdrow = sum_withdrow
            )
        if not create:
            logger.error(f"Не был добавлен юзер {user_id} в бд заявок")
            return ResultValidation("Ошибка", True)
    
        user_db_crud = UserDBCrud(user_id, db_session)
    
        balance_update = await user_db_crud.subtract_balance(sum_withdrow)
        if not balance_update:
            logger.error(f"Баланс пользователя {user_id} не был обновлен")
            return ResultValidation("Ошибка", True)
    
        return ResultValidation(
            "Успешно! Ваша заявка на вывод была добавлена, после того как администраторы отправят вам деньги, мы вам сообщим!\n"
            "Пока ваша заявка расматривается, вам нельзя делать вывод средств",
            False,
            reply_markup=back_menu_card_bt()
            )
        
class SumWithdraw:
    def __init__(self):
        pass
    
    async def handle_sum_withdraw(
        self,
        sum_w: str,
        db_session: AsyncSession,
        user_id: str | int
    ) -> ResultValidation:
        if not sum_w.isdigit():
            return ResultValidation(
                "Пожалуйста, введите число",
                True,
                reply_markup=back_menu_card_bt()
                )
    
        user_db_crud = UserDBCrud(user_id, db_session)
    
        balance_user = await user_db_crud.get_user_balance_or_zero()
        if balance_user == 0:
            return ResultValidation(
                "У вас баланс равняется 0, пожалуйста перейдите в меню",
                True,
                reply_markup=back_menu_card_bt()
                )
        
        if balance_user > int(sum_w):
            return ResultValidation(
                f"Извините, но введенная сумма {sum_w} больше, чем у вас есть {balance_user}, повторите попытку еще раз",
                True,
                reply_markup=back_menu_card_bt()
                )
    
        return ResultValidation(
            "Теперь введите ваш полный адрес криптокошелька:",
            False,
            reply_markup=back_menu_card_bt()
            )
        
class Withdraw:
    def __init__(self):
        pass
    
    async def handle_withdraw(
        self,
        db_session: AsyncSession,
        user_id: str | int,
    ) -> ResultValidation:
        user_db_crud = UserDBCrud(user_id, db_session)
    
        result_balance = await user_db_crud.get_user_balance_or_zero()
        if result_balance == 0:
            return ResultValidation("Ваш баланс равняется 0", True)
    
        application_user = await user_db_crud.get_application_user()
        if application_user:
            return ResultValidation("У вас уже есть активная заявка", True)
    
        return ResultValidation(
            "Пожалуйста укажите сумму вывода, либо нажмите на кнопку, чтобы вывести всю сумму:",
            False,
            reply_markup=sum_withdrow(result_balance),
            call_message_answer_return=True
            )