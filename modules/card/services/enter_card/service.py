from modules.card.services.enter_card.handlers import EnterCard, SendOnAdmin

class EnterCardService:
    def __init__(self):
        self.enter_card = EnterCard()
        self.send_on_admin = SendOnAdmin()