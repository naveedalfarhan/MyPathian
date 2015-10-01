from datetime import datetime
from api.models.User import User
import pytz
import rethinkdb as r


class UserRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.users

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get_user_by_username(self, username):
        users = self.uow.run_list(self.table.filter({"username": username}))
        if len(users) < 1:
            return None
        else:
            return User(user_dict=users[0])

    def get_user_by_id(self, id):
        return self.uow.run(self.table.get(id))

    def get_users_by_ids(self, ids):
        return self.uow.run(self.table.get_all(*ids))

    def add_user(self, user, created_by):
        roles = user.roles
        del user.roles
        user.created_date = datetime.utcnow().replace(tzinfo=pytz.utc)
        user.created_by = created_by
        insert = self.uow.run(self.table.insert({"username": user.username, "password": user.password,
                                                 "created_by": user.created_by, "created_date": user.created_date,
                                                 "primary_group_id": user.primary_group_id,
                                                 "group_ids": user.group_ids, "active": user.active,
                                                 "expiration_date": user.expiration_date,
                                                 "email": user.email,
                                                 "address": user.address, "city": user.city,
                                                 "state": user.state, "zip":user.zip,
                                                 "first_name": user.first_name, "last_name": user.last_name,
                                                 "job_title": user.job_title}))
        user_id = insert['generated_keys'][0]
        for r in roles:
            self.uow.run(self.uow.tables.users_roles.insert({"user_id": user_id, "role_id": r}))

    def update_user_login_time(self, id):
        self.uow.run(self.table.get(id).update({"last_login_date": datetime.now().replace(tzinfo=pytz.utc)}))

    def add_create_audit(self, id, creator):
        user = self.uow.run(self.table.get(id).update({"created_date": datetime.utcnow(), "created_by": creator}))

    def update_user(self, updater, user):
        # Handle the update manually to avoid overwriting password
        roles = user.roles
        del user.roles
        update_dict = dict(last_modified_on=datetime.now().replace(tzinfo=pytz.utc), last_modified_by=updater,
                           username=user.username, primary_group_id=user.primary_group_id, group_ids=user.group_ids,
                           active=user.active, expiration_date=user.expiration_date, email=user.email, address=user.address,
                           city=user.city, state=user.state, zip=user.zip, first_name=user.first_name, last_name=user.last_name,
                           job_title=user.job_title)
        if user.password:
            update_dict['password'] = user.password
        self.uow.run(self.table.get(user.id).update(update_dict))
        self.uow.run(self.uow.tables.users_roles.filter({"user_id": user.id}).delete())

        for r in roles:
            self.uow.run(self.uow.tables.users_roles.insert({"user_id": user.id, "role_id": r["id"]}))

    def delete_user(self, id):
        self.uow.run(self.table.get(id).delete())
        self.uow.run(self.table.filter({"user_id": id}).delete())

    def get_users_roles(self, id):
        roles = self.uow.run_list(self.uow.tables.users_roles
                                  .eq_join("user_id", self.table).zip()
                                  .eq_join("role_id", self.uow.tables.roles).zip()
                                  .filter({"user_id": id})
                                  .pluck("role_id", "name", "permissions")
                                  .map(lambda record: {'name': record['name'], 'id': record['role_id'],
                                                       'permissions': record['permissions']}))
        return roles

    def user_exists(self, name):
        return not self.uow.run(self.table.filter({"username": name}).is_empty())

    def user_exists_with_id(self, username, user_id):
        return not self.uow.run(self.table
                                .filter((r.row['username'] == username) & (r.row['id'] != user_id)).is_empty())

    def get_groups(self, id):
        groups = []
        user = self.uow.run(self.table.get(id))
        if 'primary_group_id' in user and user['primary_group_id']:
            groups.append(user['primary_group_id'])
        if 'group_ids' in user:
            groups += user['group_ids']
        return list(set(groups))

    def get_notifications_for_user(self, id):
        return self.uow.run_list(self.uow.tables.active_notifications.get_all(id, index='user_id'))

    def delete_notification(self, notificationId):
        self.uow.run(self.uow.tables.active_notifications.get(notificationId).delete())
