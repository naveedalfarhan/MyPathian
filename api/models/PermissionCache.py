from db.uow import UoW


class PermissionCache:
    cache = {}

    @classmethod
    def update_user_permission_cache(cls, user_id, uow):
        roles = uow.users.get_users_roles(user_id)
        permissions = []

        # get all the permissions for each role
        for r in roles:
            permissions += r['permissions']

        # make the list of permissions unique
        permissions = list(set(permissions))

        # update user_id in dictionary with permission list
        cls.cache[user_id] = permissions

    @classmethod
    def user_has_permissions(cls, user_id, required_permissions, uow):
        if user_id not in cls.cache:
            cls.update_user_permission_cache(user_id, uow)
        permissions = cls.cache[user_id]
        for p in required_permissions:
            if p not in permissions:
                return False
        return True

    @classmethod
    def user_has_any_permission(cls, user_id, possible_permissions, uow):
        if user_id not in cls.cache:
            cls.update_user_permission_cache(user_id, uow)
        permissions = cls.cache[user_id]
        for p in possible_permissions:
            if p in permissions:
                return True
        return False

    @classmethod
    def clear_permission_cache(cls):
        cls.cache = {}

    @classmethod
    def remove_user_from_cache(cls, user_id):
        if user_id in cls.cache:
            del cls.cache[user_id]

    @classmethod
    def get_permissions_for_user(cls, user_id, uow):
        if user_id not in cls.cache:
            cls.update_user_permission_cache(user_id, uow)
            return cls.cache[user_id]
        else:
            return cls.cache[user_id]