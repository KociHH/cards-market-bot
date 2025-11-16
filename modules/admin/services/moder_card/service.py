from modules.admin.services.moder_card.handlers import Change, Add, Delete

class ModerCardService:
    def __init__(self):
        self.add = Add()
        self.change = Change()
        self.delete = Delete()