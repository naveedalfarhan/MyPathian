import json
import bcrypt
import rethinkdb as r

class DatabaseCreator:
    def __init__(self, conn, db_name):
        self.conn = conn
        self.db_name = db_name

    def __load_db_structure(self):
        json_data_file = open("db_structure.json")
        self.db_structure = json.load(json_data_file)
        json_data_file.close()

    def __build_db_structure(self):
        if not r.db_list().contains(self.db_name).run(self.conn):
            r.db_create(self.db_name).run(self.conn)

        for table_def in self.db_structure["tables"]:
            self.__create_table(table_def)

    def __create_table(self, table_def):
        table_name = None
        if type(table_def) == str or type(table_def) == unicode:
            table_name = table_def
            table_def = None
        elif type(table_def) == dict:
            table_name = table_def["name"]
        else:
            table_def = None

        table_created = False

        if table_name:
            if not r.db(self.db_name).table_list().contains(table_name).run(self.conn):
                r.db(self.db_name).table_create(table_name).run(self.conn)
                table_created = True

                if table_def is not None and "seed_data" in table_def and table_created:
                    r.db(self.db_name).table(table_name).insert(table_def["seed_data"]).run(self.conn)

            if table_def:
                if "indexes" in table_def:
                    for index_def in table_def["indexes"]:
                        self.__create_index(table_name, index_def)

    def __create_index(self, table_name, index_def):
        index_name = None
        if type(index_def) == str or type(index_def) == unicode:
            index_name = index_def
            index_def = None
        elif type(index_def) == dict:
            index_name = index_def["name"]
        else:
            index_def = None

        if index_name:
            if not r.db(self.db_name).table(table_name).index_list().contains(index_name).run(self.conn):
                if index_def:
                    multi = False
                    if "multi" in index_def and index_def["multi"]:
                        multi = True

                    if "fields" in index_def:
                        index_fields = []
                        for index_field in index_def["fields"]:
                            index_fields.append(r.row[index_field])
                        r.db(self.db_name).table(table_name).index_create(index_name, index_fields, multi=multi).run(self.conn)
                    else:
                        r.db(self.db_name).table(table_name).index_create(index_name, multi=multi).run(self.conn)
                else:
                    r.db(self.db_name).table(table_name).index_create(index_name).run(self.conn)



    def run(self):
        self.__load_db_structure()
        self.__build_db_structure()

        if r.db(self.db_name).table("users").filter({"username": "admin"}).is_empty().run(self.conn):
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw("kingston", salt)
            username = "admin"
            result = r.db(self.db_name).table("users").insert(
                {"username": username, "password": password, "primary_group_id": "0", "group_ids": [],
                 "active": True}).run(self.conn)
            admin_user_id = result['generated_keys'][0]
        else:
            admin_user = list(r.db(self.db_name).table("users").filter({"username": "admin"}).run(self.conn))[0]
            admin_user_id = admin_user["id"]

        if r.db(self.db_name).table("roles").filter({"name": "Administrator"}).is_empty().run(self.conn):
            role = {
                "name": "Administrator",
                "permissions": [
                    "Manage Users",
                    "View Users",
                    "Manage Roles",
                    "View Roles",
                    "Manage Weather Stations",
                    "View Weather Stations",
                    "Manage Groups",
                    "View Groups",
                    "Manage Group Mappings",
                    "View Group Mappings",
                    "Manage Accounts",
                    "View Accounts",
                    "Manage Component Structure Tree",
                    "View Component Structure Tree",
                    "Manage Component Mapping Tree",
                    "View Component Mapping Tree",
                    "Manage Component Points",
                    "View Component Points",
                    "Manage Component Engineering",
                    "View Component Engineering",
                    "Manage Meeting Types",
                    "View Meeting Types",
                    "Manage Utility Companies",
                    "View Utility Companies",
                    "Manage Action Item Priorities",
                    "View Action Item Priorities",
                    "Manage Action Item Types",
                    "View Action Item Types",
                    "Manage Action Item Statuses",
                    "View Action Item Statuses",
                    "Manage Task Priorities",
                    "View Task Priorities",
                    "Manage Task Statuses",
                    "View Task Statuses",
                    "Manage Task Types",
                    "View Task Types",
                    "Manage Issue Priorities",
                    "View Issue Priorities",
                    "Manage Issue Statuses",
                    "View Issue Statuses",
                    "Manage Issue Types",
                    "View Issue Types",
                    "Manage Equipment",
                    "View Equipment",
                    "Manage Categories",
                    "View Categories",
                    "Manage Contacts",
                    "View Contacts",
                    "Manage Tasks",
                    "View Tasks",
                    "Manage Issues",
                    "View Issues",
                    "Manage Projects",
                    "View Projects",
                    "Manage ECO",
                    "View ECO",
                    "Manage Committees",
                    "View Committees",
                    "Manage Meetings",
                    "View Meetings",
                    "Upload Group Data",
                    "Run Group Reports",
                    "Run NAICS Reports",
                    "Run SIC Reports",
                    "Run Component Reports",
                    "Run Subcomponent Reports",
                    'Run Bronze Reports',
                    "View Dashboard",
                    "Manage Reset Schedules",
                    "View Reset Schedules"
                ]
            }
            result = r.db(self.db_name).table("roles").insert(role).run(self.conn)
            admin_role_id = result['generated_keys'][0]
        else:
            admin_role = list(r.db(self.db_name).table("roles").filter({"name": "Administrator"}).run(self.conn))[0]
            admin_role_id = admin_role["id"]

        if r.db(self.db_name).table("users_roles").filter(
                {"user_id": admin_user_id, "role_id": admin_role_id}).is_empty().run(self.conn):
            r.db(self.db_name).table("users_roles").insert({"user_id": admin_user_id, "role_id": admin_role_id}).run(self.conn)