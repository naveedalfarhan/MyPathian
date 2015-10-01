from db.uow import UoW

__author__ = 'badams'


class ReportingGroupCache:
    cache = {}

    @classmethod
    def update_reporting_group_cache(cls, user_id, uow):
        user = uow.users.get_user_by_id(user_id)

        primary_group = uow.groups.get_group_by_id(user['primary_group_id'])

        if primary_group:
            cls.cache[user_id] = primary_group.__dict__
        else:
            cls.cache[user_id] = None

    @classmethod
    def clear_group_cache(cls):
        cls.cache = {}

    @classmethod
    def get_user_group(cls, user_id, uow):
        if user_id not in cls.cache:
            cls.update_reporting_group_cache(user_id, uow)
        return cls.cache[user_id]

    @classmethod
    def change_reporting_group(cls, user_id, group_id, uow):
        group = uow.groups.get_group_by_id(group_id)

        cls.cache[user_id] = group.__dict__