import unittest
from db.repositories.component_point_repository import ComponentPointRepository
from mock import Mock, patch

__author__ = 'badams'


class TestComponentPointRepository(unittest.TestCase):
    def setUp(self):
        self.uow = Mock()
        self.repo = ComponentPointRepository(self.uow)

    def test_get_by_component_point_num(self):
        point_id = Mock()

        table_mock = self.uow.tables.component_points

        rv = self.repo.get_by_component_point_num(point_id)

        table_mock.get_all.assert_called_with(point_id, index='component_point_num')
        self.uow.run_list.assert_called_with(table_mock.get_all.return_value)

        self.assertEqual(rv, self.uow.run_list.return_value)

    def test_revoke_master_point(self):
        point_id = Mock()

        table_mock = self.uow.tables.component_points
        rv = self.repo.revoke_master_point(point_id)

        # table.get()
        table_mock.get.assert_called_with(point_id)
        return_value = table_mock.get.return_value

        # table.get().update()
        return_value.update.assert_called_with({"master_point": False})
        return_value = return_value.update.return_value

        self.uow.run.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run.return_value)

    def test_delete_component_master_point_mappings_for_point(self):
        master_point_num = Mock()

        mapping_table_mock = self.uow.tables.component_master_point_mappings

        rv = self.repo.delete_component_master_point_mappings_for_point(master_point_num)

        # table.get_all()
        mapping_table_mock.get_all.assert_called_with(master_point_num, index="master_point_num")
        return_value = mapping_table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run.return_value)

    @patch("db.repositories.component_point_repository.ComponentPointRepository.unit_map_func")
    def test_all_of_same_unit(self, unit_map_func):
        component_point_ids = [Mock(), Mock(), Mock()]
        component_points = [
            {
                'id': component_point_ids[0],
                'units': 'Test1'
            },
            {
                'id': component_point_ids[1],
                'units': 'Test1'
            },
            {
                'id': component_point_ids[2],
                'units': 'Test1'
            }
        ]

        table_mock = self.uow.tables.component_points

        self.uow.run_list.return_value = ['Test1']

        rv = self.repo.all_of_same_unit(component_point_ids)

        # table.get_all()
        table_mock.get_all.assert_called_with(*component_point_ids)
        return_value = table_mock.get_all.return_value

        # table.get_all().has_fields()
        return_value.has_fields.assert_called_with('units')
        return_value = return_value.has_fields.return_value

        # table.get_all().has_fields().map()
        return_value.map.assert_called_with(unit_map_func)
        return_value = return_value.map.return_value

        # table.get_all().has_fields().map().distinct()
        return_value.distinct.assert_called_with()
        return_value = return_value.distinct.return_value

        self.uow.run_list.assert_called_with(return_value)

        self.assertEqual(rv, True)

    @patch("db.repositories.component_point_repository.ComponentPointRepository.unit_map_func")
    def test_all_of_same_unit_fail(self, unit_map_func):
        component_point_ids = [Mock(), Mock(), Mock()]
        component_points = ['Test1', 'Test2']

        table_mock = self.uow.tables.component_points

        # set up the return values
        self.uow.run_list.return_value = component_points

        rv = self.repo.all_of_same_unit(component_point_ids)

        self.assertEqual(rv, False)

    def test_unit_map_func(self):
        record = {
            'id': Mock(),
            'units': 'Test1'
        }

        rv = self.repo.unit_map_func(record)

        self.assertEqual(rv, 'Test1')

    @patch("db.repositories.component_point_repository.ComponentPointRepository.unit_map_func")
    def test_group_by_units(self, unit_map_func):
        component_point_ids = [Mock(), Mock(), Mock()]

        table_mock = self.uow.tables.component_points

        rv = self.repo.group_by_units(component_point_ids)

        # table.get_all()
        table_mock.get_all.assert_called_with(*component_point_ids)
        return_value = table_mock.get_all.return_value

        # table.get_all().group()
        return_value.group.assert_called_with(unit_map_func)
        return_value = return_value.group.return_value

        # table.get_all().group().ungroup()
        return_value.ungroup.assert_called_with()
        return_value = return_value.ungroup.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    @patch("db.repositories.component_point_repository.ComponentPointRepository.syrx_map_func")
    def test_get_syrx_nums_for_component_point(self, syrx_map_func):
        component_point_id = Mock()

        table_mock = self.uow.tables.equipment_points

        rv = self.repo.get_syrx_nums_for_component_point(component_point_id)

        # table.get_all()
        table_mock.get_all.assert_called_with(component_point_id, index='component_point_num')
        return_value = table_mock.get_all.return_value

        # table.get_all().map()
        return_value.map.assert_called_with(syrx_map_func)
        return_value = return_value.map.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    def test_syrx_map_func(self):
        record = {
            'id': Mock(),
            'syrx_num': Mock(),
            'component_point_id': Mock()
        }

        rv = self.repo.syrx_map_func(record)

        self.assertEqual(rv, record['syrx_num'])