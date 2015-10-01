__author__ = 'badams'


class SavedReportConfigurationRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.saved_report_configurations

    def get_configurations_for_user(self, user_id):
        return self.uow.run_list(self.table.get_all(user_id, index='user_id'))

    def insert_configuration(self, config):
        new_id = self.uow.run(self.table.insert(config))['generated_keys'][0]
        return new_id

    def get_configuration_by_name(self, user_id, name):
        return self.uow.run_list(self.table.get_all(user_id, index='user_id').filter({'name': name}))

    def get_configuration_by_id(self, config_id):
        return self.uow.run(self.table.get(config_id))

    def delete_configuration(self, config_id):
        return self.uow.run(self.table.get(config_id).delete())

    def get_configuration_by_type(self, user_id, report_type):
        return self.uow.run_list(self.table.get_all(user_id, index='user_id').filter({'report_type': report_type}))