from api.models.PriceNormalization import PriceNormalization
from rethinkdb import desc


class PriceNormalizationRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.pricenormalizations

    def get_all(self, query_parameters=None):
        if query_parameters is None:
            return self.uow.run_list(self.table)
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get_all_by_account(self, accountid, query_parameters=None):
        if query_parameters is None:
            return self.uow.run_list(self.table.get_all(accountid, index='account_id'))
        table = self.table.filter({"account_id": accountid})
        return self.uow.apply_query_parameters(table, query_parameters)

    def get_by_id(self, model_id):
        model_raw = self.uow.run(self.table.get(model_id))
        model = PriceNormalization(model_raw)
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
        # if there is only one entry, do not allow the deletion
        model = self.get_by_id(model_id)
        if self.uow.run(self.table.get_all(model.account_id, index="account_id").count()) < 1:
            raise Exception("Cannot delete only price normalization.")
        self.uow.run(self.table.get(model_id).delete())

    def get_most_recent_for_account(self, account_id):
        model_raw = self.uow.run_list(self.table.get_all(account_id, index='account_id').order_by(desc('effective_date')))
        if len(model_raw) < 1:
            return None

        model = PriceNormalization(model_raw[0])
        return model