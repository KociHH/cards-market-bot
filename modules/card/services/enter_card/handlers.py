from modules.shared.services.validation.result import ResultValidation
from modules.card.crud.user import UserDBCrud
from sqlalchemy.ext.asyncio import AsyncSession
from modules.card.keyboards.reply.buttons import send_on_admin_bt
import logging
from modules.card.crud.create import CreateDBCrud
from modules.card.keyboards.inline.buttons import back_menu_card_inline_bt


logger = logging.getLogger(__name__)

class SendOnAdmin:
    def __init__(self):
        pass
    
    async def handle_send_on_admin(
        self,
        db_session: AsyncSession,
        card_data: dict
        ) -> ResultValidation:
        
        name = card_data.get("name")
        price = card_data.get("price")
        description = card_data.get("description")
        user_id = card_data.get("user_id")
    
        if not all([name, price, description, user_id]):
            logger.error(f"Не хватает нескольких параметров карточки в card_data: {card_data}")
            return ResultValidation("Ошибка: не все данные сохранены. Попробуйте создать карточку заново", True)
    
        creare_db_crud = CreateDBCrud(db_session)
    
        create = await creare_db_crud.create_card_moder(
            name = name,
            price = price,
            description = description,
            user_id = user_id
        )
        if not create:
            logger.error("Не создалась карточка товара для добавления в бд на проверку")
            return ResultValidation("Ошибка", True) 
        
        return ResultValidation(
            "Карточка товара успешно добавлена на проверку администрации!\n"
            "Когда решит администрация добавить карту с изменениями или без, то мы вам сообщим.\n",
            False,
            {},
            back_menu_card_inline_bt()
            ) 


class EnterCard:
    def __init__(self):
        pass
    
    async def handle_enter_card(
        self,
        user_text: str,
        user_id: str | int,
        db_session: AsyncSession
    ) -> ResultValidation:
        name = None
        price = None
        description = None
    
        lines = user_text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("name-"):
                name = line.split("-", 1)[1].strip()
            elif line.startswith("price-"):
                price = line.split("-", 1)[1].strip()
            elif line.startswith("description-"):
                description = line.split("-", 1)[1].strip()
    
        if not name or not price or not description:
            return ResultValidation("Вы ввели не все обязательные параметры! Попробуйте еще раз", True)
    
        try:
            price = int(price)
        except ValueError:
            return ResultValidation("Введите пожалуйста корректное число цены", True)
    
        if price <= 0:
            return ResultValidation("Цена должна быть больше нуля", True)
        
        if price < 80:
            return ResultValidation(f"Минимальная цена карточки для оплаты составляет 80 рублей. Повторите попытку", True)
    
        if price > 1000000:
            return ResultValidation("Цена не может превышать 1 000 000 рублей", True)
    
        user_db_crud = UserDBCrud(user_id, db_session)
    
        if_indices_card, if_indices_moder = await user_db_crud.get_card_moder(name, description)
        if if_indices_card or if_indices_moder:
            return ResultValidation("У вас уже существует или уже расматривается индетичная карточка, пожалуйста измените параметры которую хотите добавить", True)
        
        return ResultValidation(
            "Отправить на рассмотрение администрации? Если нет, то продолжайте изменять параметры карточки", 
            False, 
            {
                "name": name,
                "price": price,
                "description": description,
                "user_id": user_id,
                }, 
            send_on_admin_bt()
            )