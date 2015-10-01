from api.models.Contact import Contact


class ContactRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.contacts

    def get_all_contacts_table(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get_all_contacts(self):
        cursor = self.uow.run(self.table)
        return list(cursor)

    def get(self, model_id):
        model_raw = self.uow.run(self.table.get(model_id))
        model = Contact(model_raw)
        return model

    def get_with_group(self, model_id):
        model_raw = self.uow.run(self.table.eq_join("id", self.uow.tables.groups).zip())
        return model_raw

    def update(self, model):
        self.uow.run(self.table.update(model.__dict__))

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        self.uow.run(self.table.insert(model.__dict__))

    def delete(self, model_id):
        self.uow.run(self.table.get(model_id).delete())

    def get_list(self, ids):
        return self.uow.run(self.table.get_all(", ".join(ids)))