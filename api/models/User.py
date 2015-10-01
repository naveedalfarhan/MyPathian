from datetime import datetime
from flask.ext.login import UserMixin


class User(UserMixin):
    def __init__(self, user_dict=None):
        self.id = None
        self.username = None
        self.password = None
        self.active = None
        self.primary_group_id = None
        self.group_ids = []
        self.last_login_date = None
        self.last_modified_on = None
        self.last_modified_by = None
        self.created_date = None
        self.created_by = None
        self.expiration_date = None
        self.email = None
        self.address = None
        self.city = None
        self.state = None
        self.zip = None
        self.first_name = None
        self.last_name = None
        self.job_title = None

        if user_dict:
            self.__dict__.update(**user_dict)
            if self.last_login_date and type(self.last_login_date) == datetime:
                self.last_login_date = self.last_login_date.strftime("%m/%d/%Y %H:%M")
            if self.last_modified_on and type(self.last_modified_on) == datetime:
                self.last_modified_on = self.last_modified_on.strftime("%m/%d/%Y %H:%M")
            if self.created_date and type(self.created_date) == datetime:
                self.created_date = self.created_date.strftime("%m/%d/%Y %H:%M")
            if self.expiration_date and type(self.expiration_date) == datetime:
                self.expiration_date = self.expiration_date.strftime("%m/%d/%Y %H:%M")

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True
