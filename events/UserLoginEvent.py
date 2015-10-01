from db.uow import UoW
from events.Event import Event

__author__ = 'brian'


class UserLoginEvent(Event):
    id = ''

    def __init__(self, user_id):
        self.id = user_id
        self.uow = UoW(False)

    def handle(self):
        # send the data to database
        self.uow.users.update_user_login_time(self.id)