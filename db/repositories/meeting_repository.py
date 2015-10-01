from api.models.Meeting import Meeting


class MeetingRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.meetings
        self.contacts_table = uow.tables.contacts
        self.groups_table = uow.tables.groups

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        self.uow.run(self.table.insert(model.__dict__))

    def get(self, id):
        model_raw = self.uow.run(self.table.get(id))
        model = Meeting(model_raw)
        model.attendees_models = []
        for a in model.attendees_ids:
            model.attendees_models.append(self.uow.run(self.contacts_table.get(a)))
        model.called_by_model = self.uow.run(self.contacts_table.get(model.called_by_id))
        model.facilitator_model = self.uow.run(self.contacts_table.get(model.facilitator_id))
        model.group_model = self.uow.run(self.groups_table.get(model.group_id))
        model.note_taker_model = self.uow.run(self.contacts_table.get(model.note_taker_id))
        model.time_keeper_model = self.uow.run(self.contacts_table.get(model.time_keeper_id))
        return model

    def update(self, model):
        self.uow.run(self.table.update(model.__dict__))

    def delete(self, id):
        self.uow.run(self.table.get(id).delete())