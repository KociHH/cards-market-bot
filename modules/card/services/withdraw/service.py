from modules.card.services.withdraw.handlers import Withdraw, SumWithdraw, EnterAddress

class WithdrawService:
    def __init__(self):
        self.sum_withdraw = SumWithdraw()
        self.enter_address = EnterAddress()
        self.withdraw = Withdraw()