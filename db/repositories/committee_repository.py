from api.models.Committee import Committee
import rethinkdb as r

class CommitteeRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.committees

    def get_all(self, query_parameters):
        query = (self.table.eq_join("group_id", self.uow.tables.groups)
                 .map(r.row.merge(lambda x: {
                     "right": {
                         "g_name": x["right"]["name"]
                     }
                 }))
                 .without({"right": {"id": True}})
                 .without({"right": {"name": True}})
                 .zip()
                 .eq_join("corporate_energy_director_id", self.uow.tables.contacts)
                 .map(r.row.merge(lambda x: {
                     "right": {
                         "c_e_d": x["right"]["full_name"]
                     }
                 }))
                 .without({"right": {"id": True}})
                 .without({"right": {"full_name": True}})
                 .zip())

        return self.uow.apply_query_parameters(query, query_parameters)

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass

        rv = self.uow.run(self.table.insert(model.__dict__))
        model_id = rv['generated_keys'][0]

        return model_id

    def get(self, model_id):
        model_raw = self.uow.run(self.table.get(model_id))
        model = Committee(model_raw)

        model.energy_director_model = self.uow.run(self.uow.tables.contacts.get(model.corporate_energy_director_id))
        model.group_model = self.uow.run(self.uow.tables.groups.get(model.group_id))

        model.facility_directors_model = []
        for f in model.facility_directors_ids:
            model.facility_directors_model.append(self.uow.run(self.uow.tables.contacts.get(f)))

        model.team_members_model = []
        for t in model.team_members_ids:
            model.team_members_model.append(self.uow.run(self.uow.tables.contacts.get(t)))

        return model

    def update(self, model):
        self.uow.run(self.table.update(model.__dict__))

    def delete(self, model_id):
        self.uow.run(self.table.get(model_id).delete())