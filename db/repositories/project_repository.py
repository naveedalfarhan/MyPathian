from api.models.Project import Project


class ProjectRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.projects

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        self.uow.run(self.table.insert(model.__dict__))

    def update(self, model):
        self.uow.run(self.table.update(model.__dict__))

    def get(self, id):
        model_raw = self.uow.run(self.table.get(id))
        model = Project(model_raw)
        return model

    def delete(self, id):
        self.uow.run(self.table.get(id).delete())

    def get_all_as_list(self):
        return self.uow.run_list(self.table.pluck("id", "name"))