from api.models.SizeNormalization import SizeNormalization


class SizeNormalizationRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.sizenormalizations

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get_all_by_account(self, accountid, query_parameters=None):
        if query_parameters is None:
            return self.uow.run_list(self.table.get_all(accountid, index='account_id'))
        table = self.table.filter({"account_id": accountid})
        return self.uow.apply_query_parameters(table, query_parameters)

    def get_by_id(self, model_id):
        model_raw = self.uow.run(self.table.get(model_id))
        model = SizeNormalization(model_raw)
        return model

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        rv = self.uow.run(self.table.insert(model.__dict__))
        model_id = rv['generated_keys'][0]
        return model_id

    def update(self, model):
        d = model.__dict__
        self.uow.run(self.table.update(d))

    def delete(self, model_id):
        self.uow.run(self.table.get(model_id).delete())