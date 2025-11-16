from modules.card.services.pay.handlers import PayCard, OnSuccessfulPayment

class PayService:
    def __init__(self):
        self.pay_card = PayCard()
        self.on_successful_payment = OnSuccessfulPayment()