from modules.admin.services.payment.handlers import PaymentCompleted

class PaymentService:
    def __init__(self):
        self.payment_completed = PaymentCompleted()