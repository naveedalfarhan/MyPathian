from api.models.ECO import Eco
import rethinkdb as r


class EcoRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.eco

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.table.eq_join("project_id", self.uow.tables.projects)
                                               .map(r.row.merge(lambda x: {"right": {"p_name": x["right"]["name"]}}))
                                               .without({"right": {"name": True}})
                                               .zip(), query_parameters)

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        self.uow.run(self.table.insert(model.__dict__))

    def update(self, model):
        self.uow.run(self.table.update(model.__dict__))

    def get(self, model_id):
        model_raw = self.uow.run(self.table.get(model_id))
        model = Eco(model_raw)
        return model

    def delete(self, model_id):
        self.uow.run(self.table.get(model_id).delete())