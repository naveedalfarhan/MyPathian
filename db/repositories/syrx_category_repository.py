from api.models.SyrxCategory import SyrxCategory


class SyrxCategoryRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.syrx_categories

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get_all_categories(self):
        return self.uow.run(self.table.order_by('name'))

    def get(self, category_id):
        model_raw = self.uow.run(self.table.get(category_id))
        model = SyrxCategory(model_raw)
        return model

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        self.uow.run(self.table.insert(model.__dict__))

    def update(self, model):
        self.uow.run(self.table.update(model.__dict__))

    def delete(self, category_id):
        self.uow.run(self.table.get(category_id).delete())

    def get_all_as_list(self):
        return self.uow.run(self.table)

    def name_exists(self, name):
        return not self.uow.run(self.table.filter({"name": name}).is_empty())
