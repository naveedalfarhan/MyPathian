from db.uow import UoW
from events.Event import Event

__author__ = 'brian'


class UserCreatedEvent(Event):
    id = ''
    creator = ''

    def __init__(self, id, creator_id):
        self.id = id
        self.creator = creator_id
        self.uow = UoW(False)

    def handle(self):
        # add user to database
        self.uow.users.add_create_audit(self.id, self.creator)