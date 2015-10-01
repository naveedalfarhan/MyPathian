from db.uow import UoW
from events.Event import Event

__author__ = 'brian'


class RoleCreatedEvent(Event):
    id = ''
    creator = ''

    def __init__(self, role_id, creator_id):
        self.id = role_id
        self.creator = creator_id
        self.uow = UoW(False)

    def handle(self):
        # send the data to database
        self.uow.roles.add_create_audit(self.id, self.creator)