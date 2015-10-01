from api.models.ActionItemPriority import ActionItemPriority


class ActionItemPriorityRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.action_item_priorities

    def get_all_actionitempriorities(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get(self, id):
        model_raw = self.uow.run(self.table.get(id))
        model = ActionItemPriority(model_raw)
        return model

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

    def does_priority_exist_by_name(self, name):
        is_in_database = False
        cursor = self.uow.run(self
                              .table
                              .filter(lambda priority: priority["name"].match("(?i)^" + name + "$")))

        # It looks like iterating through a cursor is the only way to check if a record was a returned with a filtered
        # query
        for record in cursor:
            is_in_database = True
            break

        return is_in_database