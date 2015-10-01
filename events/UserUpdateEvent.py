from db.uow import UoW
from events.Event import Event

__author__ = 'brian'


class UserUpdateEvent(Event):
    id = ''
    updater = ''

    def __init__(self, user_id, updater_id):
        self.id = user_id
        self.updater = updater_id
        self.uow = UoW(False)

    def handle(self):
        # send the data to database
        self.uow.users.update_user_audit(self.id, self.updater)