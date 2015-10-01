class Notification:
    def __init__(self, p=None):
        self.id = None
        self.user_id = None
        self.text = None

        if p:
            self.__dict__.update(**p)