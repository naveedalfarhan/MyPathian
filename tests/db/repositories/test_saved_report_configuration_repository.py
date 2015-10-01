import unittest
from db.repositories.saved_report_configuration_repository import SavedReportConfigurationRepository
from mock import Mock, MagicMock

__author__ = 'badams'


class TestSavedReportConfigurationRepository(unittest.TestCase):
    def setUp(self):
        self.uow = MagicMock()
        self.repo = SavedReportConfigurationRepository(self.uow)

    def test_get_configurations_for_user(self):
        user_id = Mock()

        table_mock = self.uow.tables.saved_report_configurations

        rv = self.repo.get_configurations_for_user(user_id)

        table_mock.get_all.assert_called_with(user_id, index='user_id')
        self.uow.run_list.assert_called_with(table_mock.get_all.return_value)

        self.assertEqual(rv, self.uow.run_list.return_value)

    def test_insert_configuration(self):
        configuration = {
            'report_type': Mock(),
            'user_id': Mock(),
            'configuration': Mock(),
            'name': Mock()
        }

        table_mock = self.uow.tables.saved_report_configurations

        rv = self.repo.insert_configuration(configuration)

        table_mock.insert.assert_called_with(configuration)
        self.uow.run.assert_called_with(table_mock.insert.return_value)

    def test_get_configuration_by_name(self):
        user_id = Mock()
        name = Mock()

        table_mock = self.uow.tables.saved_report_configurations

        rv = self.repo.get_configuration_by_name(user_id, name)

        # table.get_all()
        table_mock.get_all.assert_called_with(user_id, index='user_id')
        return_value = table_mock.get_all.return_value

        #table.get_all().filter()
        return_value.filter.assert_called_with({'name': name})
        return_value = return_value.filter.return_value

        self.uow.run_list.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run_list.return_value)

    def test_get_configuration_by_id(self):
        config_id = Mock()

        table_mock = self.uow.tables.saved_report_configurations

        rv = self.repo.get_configuration_by_id(config_id)

        table_mock.get.assert_called_with(config_id)

        self.uow.run.assert_called_with(table_mock.get.return_value)
        self.assertEqual(rv, self.uow.run.return_value)

    def test_remove_configuration(self):
        config_id = Mock()

        table_mock = self.uow.tables.saved_report_configurations

        self.repo.delete_configuration(config_id)

        # table.get()
        table_mock.get.assert_called_with(config_id)
        return_value = table_mock.get.return_value

        #table.get().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)

    def test_get_by_type(self):
        config_type = Mock()
        user_id = Mock()

        table_mock = self.uow.tables.saved_report_configurations

        rv = self.repo.get_configuration_by_type(user_id, config_type)

        # table.get_all()
        table_mock.get_all.assert_called_with(user_id, index='user_id')
        return_value = table_mock.get_all.return_value

        # table.get_all().filter()
        return_value.filter.assert_called_with({'report_type':config_type})
        return_value = return_value.filter.return_value

        self.uow.run_list.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run_list.return_value)