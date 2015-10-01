import unittest
from db.repositories.component_repository import ComponentRepository
from mock import Mock, patch

__author__ = 'badams'


class TestComponentRepository(unittest.TestCase):
    def setUp(self):
        self.uow = Mock()
        self.repo = ComponentRepository(self.uow)

    def test_set_component_master_point(self):
        component_id = Mock()
        master_point = Mock()

        table_mock = self.uow.tables.components

        rv = self.repo.set_component_master_point(component_id, master_point)

        # table.get()
        table_mock.get.assert_called_with(component_id)
        return_value = table_mock.get.return_value

        # table.get().update()
        return_value.update.assert_called_with({"master_point": master_point.__dict__})
        return_value = return_value.update.return_value

        self.uow.run.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run.return_value)

    def test_get_component_ancestors(self):
        component_id = Mock()

        flat_table_mock = self.uow.tables.flat_components

        rv = self.repo.get_component_ancestors(component_id)

        # table.get_all()
        flat_table_mock.get_all.assert_called_with(component_id, index='descendant_component_id')
        return_value = flat_table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run_list.return_value)

    def test_get_component_master_point_mappings(self):
        component_id = Mock()
        mapping_table_mock = self.uow.tables.component_master_point_mappings

        rv = self.repo.get_component_master_point_mappings(component_id)

        mapping_table_mock.get_all.assert_called_with(component_id, index='component_id')
        self.uow.run_list.assert_called_with(mapping_table_mock.get_all.return_value)

        self.assertEqual(rv, self.uow.run_list.return_value)

    @patch("db.repositories.component_repository.ComponentRepository.get_component_ancestors")
    def test_insert_new_component_master_point_mappings(self, get_component_ancestors):
        master_point_id = Mock()
        component_id = Mock()

        mapping_table_mock = self.uow.tables.component_master_point_mappings

        ancestor_list = [{"component_id": Mock(), "descendant_component_id": Mock()},
                         {"component_id": Mock(), "descendant_component_id": Mock()},
                         {"component_id": Mock(), "descendant_component_id": Mock()}]
        get_component_ancestors.return_value = ancestor_list

        mapping_list = [{"component_id": ancestor["component_id"],
                         "master_point_num": master_point_id} for ancestor in ancestor_list]

        rv = self.repo.insert_new_component_master_point_mappings(component_id, master_point_id)
        get_component_ancestors.assert_called_with(component_id)

        # table.insert()
        mapping_table_mock.insert.assert_called_with(mapping_list)
        return_value = mapping_table_mock.insert.return_value

        self.uow.run.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run.return_value)

    def test_descendant_component_id_mapping_func(self):
        record = {
            "component_id": Mock(),
            "descendant_component_id": '1',
            "id": Mock()
        }
        rv = self.repo.descendant_component_id_mapping_func(record)
        self.assertEqual(rv, '1')

    @patch("db.repositories.component_repository.ComponentRepository.descendant_component_id_mapping_func")
    def test_get_component_descendants(self, descendant_component_id_mapping_func):
        component_id = Mock()
        table_mock = self.uow.tables.flat_components

        rv = self.repo.get_component_descendants(component_id)

        # table.get_all()
        table_mock.get_all.assert_called_with(component_id, index='component_id')
        return_value = table_mock.get_all.return_value

        # table.get_all().map()
        return_value.map.assert_called_with(descendant_component_id_mapping_func)
        return_value = return_value.map.return_value

        self.uow.run_list.assert_called_with(return_value)
        self.assertEqual(rv, self.uow.run_list.return_value)