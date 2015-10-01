from datetime import datetime
from api.models.Role import Role
import pytz


class RoleRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.roles

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get_role_by_id(self, id):
        model_raw = self.uow.run(self.table.get(id).pluck("name", "id", "permissions"))
        return Role(model_raw)

    def role_exists(self, name):
        return not self.uow.run(self.table.filter({"name": name}).is_empty())

    def insert(self, role, creator):
        return self.uow.run(self.table.insert({"name": role.name,
                                               "created_date": datetime.utcnow().replace(tzinfo=pytz.utc),
                                               "created_by": creator, "permissions": role.permissions}))

    def update(self, role, updater):
        return self.uow.run(self.table.get(role.id)
                            .update({"name": role.name, "permissions": role.permissions,
                                     "last_modified_on": datetime.utcnow().replace(tzinfo=pytz.utc),
                                     "last_modified_by": updater}))

    def delete(self, id):
        self.uow.run(self.uow.table.users_roles.filter({"role_id": id}).delete())
        return self.uow.run(self.table.get(id).delete())

    def get_all_roles(self):
        return self.uow.run(self.table.pluck("name", "id"))

    def add_create_audit(self, id, creator):
        self.uow.run(self.table.get(id).update({"created_on": datetime.utcnow(), "created_by": creator}))
        return True

    def update_audit(self, id, updater):
        self.uow.run(self.table.get(id).update({"last_updated": datetime.utcnow(), "updated_by": updater}))
        return True