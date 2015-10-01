from datetime import datetime
import unittest
from db.repositories.compiled_point_record_repository import CompiledPointRecordRepository
from mock import Mock, patch, MagicMock


class TestCompiledPointRecordRepository(unittest.TestCase):
    def setUp(self):
        self.uow = Mock()
        self.repo = CompiledPointRecordRepository(self.uow)

    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.get_all_compiled_point_data")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.get_demand_compiled_point_data")
    def test_get_compiled_point_data(self, get_demand_compiled_point_data, get_all_compiled_point_data):
        point_nums = Mock()
        report_year = Mock()
        comparison_type = Mock()

        self.repo.get_compiled_point_data(point_nums, report_year, comparison_type, "peak")
        get_demand_compiled_point_data.assert_called_with(point_nums, report_year, comparison_type, "peak")

        self.repo.get_compiled_point_data(point_nums, report_year, comparison_type, "offpeak")
        get_demand_compiled_point_data.assert_called_with(point_nums, report_year, comparison_type, "offpeak")

        self.repo.get_compiled_point_data(point_nums, report_year, comparison_type, "all")
        get_all_compiled_point_data.assert_called_with(point_nums, report_year, comparison_type)

    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.point_num_value_group_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.mapping_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.reduce_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.final_mapping_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.point_num_group_func")
    def test_get_all_compiled_point_data(self, point_num_group_func, final_mapping_func, reduce_func, mapping_func, point_num_value_group_func):
        point_nums = [Mock(), Mock(), Mock(), Mock()]
        report_year = Mock()
        comparison_type = Mock()

        table_mock = self.uow.tables.compiled_equipment_point_records

        rv = self.repo.get_all_compiled_point_data(point_nums, report_year, comparison_type)

        expected_index_list = [
            [point_nums[0], comparison_type, report_year],
            [point_nums[1], comparison_type, report_year],
            [point_nums[2], comparison_type, report_year],
            [point_nums[3], comparison_type, report_year]
        ]

        # table.get_all()
        table_mock.get_all.assert_called_with(*expected_index_list, index="point_no_peak")
        return_value = table_mock.get_all.return_value

        # table.get_all().group()
        return_value.group.assert_called_with(point_num_value_group_func)
        return_value = return_value.group.return_value

        # table.get_all().group().map()
        return_value.map.assert_called_with(mapping_func)
        return_value = return_value.map.return_value

        # table.get_all().group().map().reduce()
        return_value.reduce.assert_called_with(reduce_func)
        return_value = return_value.reduce.return_value

        # table.get_all().group().map().reduce().ungroup()
        return_value.ungroup.assert_called_with()
        return_value = return_value.ungroup.return_value

        # table.get_all().group().map().reduce().ungroup().map()
        return_value.map.assert_called_with(final_mapping_func)
        return_value = return_value.map.return_value

        # table.get_all().group().map().reduce().ungroup().map().group()
        return_value.group.assert_called_with(point_num_group_func)
        return_value = return_value.group.return_value

        # table.get_all().group().map().reduce().ungroup().map().group().ungroup()
        return_value.ungroup.assert_called_with()
        return_value = return_value.ungroup.return_value

        self.uow.run_list.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run_list.return_value)

    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.point_num_value_group_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.mapping_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.reduce_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.final_mapping_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.point_num_group_func")
    def test_get_demand_compiled_point_data(self, point_num_group_func, final_mapping_func, reduce_func, mapping_func, point_num_value_group_func):
        point_nums = [Mock(), Mock(), Mock(), Mock()]
        report_year = Mock()
        comparison_type = Mock()
        demand_type = Mock()

        table_mock = self.uow.tables.compiled_equipment_point_records

        rv = self.repo.get_demand_compiled_point_data(point_nums, report_year, comparison_type, demand_type)

        expected_index_list = [
            [point_nums[0], comparison_type, report_year, demand_type],
            [point_nums[1], comparison_type, report_year, demand_type],
            [point_nums[2], comparison_type, report_year, demand_type],
            [point_nums[3], comparison_type, report_year, demand_type]
        ]

        # table.get_all()
        table_mock.get_all.assert_called_with(*expected_index_list, index="point_has_peak")
        return_value = table_mock.get_all.return_value

        # table.get_all().group()
        return_value.group.assert_called_with(point_num_value_group_func)
        return_value = return_value.group.return_value

        # table.get_all().group().map()
        return_value.map.assert_called_with(mapping_func)
        return_value = return_value.map.return_value

        # table.get_all().group().map().reduce()
        return_value.reduce.assert_called_with(reduce_func)
        return_value = return_value.reduce.return_value

        # table.get_all().group().map().reduce().ungroup()
        return_value.ungroup.assert_called_with()
        return_value = return_value.ungroup.return_value

        # table.get_all().group().map().reduce().ungroup().map()
        return_value.map.assert_called_with(final_mapping_func)
        return_value = return_value.map.return_value

        # table.get_all().group().map().reduce().ungroup().map().group()
        return_value.group.assert_called_with(point_num_group_func)
        return_value = return_value.group.return_value

        # table.get_all().group().map().reduce().ungroup().map().group().ungroup()
        return_value.ungroup.assert_called_with()
        return_value = return_value.ungroup.return_value

        self.uow.run_list.assert_called_with(return_value)

        self.assertEqual(rv, self.uow.run_list.return_value)

    def test_get_compiled_point_data_return_data(self,):
        data_list = [{'group': {'point_num': Mock()}, 'reduction': [{'comparison_value': Mock(), 'sum_value': Mock()},
                                                                    {'comparison_value': Mock(), 'sum_value': Mock()}]}]

        rv = self.repo.format_for_kendo(data_list)

        self.assertTrue(len(rv) > 0)
        for entry in rv:
            self.assertTrue('name' in entry)
            self.assertTrue('data' in entry)
            self.assertTrue(len(entry['data']) > 0)
            for data_entry in entry['data']:
                self.assertEqual(2, len(data_entry))

    def test_point_num_value_group_func(self):
        record = {
            "point_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock()
        }

        func_return = self.repo.point_num_value_group_func(record)
        self.assertTrue('point_num' in func_return)
        self.assertTrue('comparison_value' in func_return)
        self.assertTrue(len(func_return.keys()) == 2)

    def test_point_num_group_func(self):
        record = {
            "point_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock()
        }

        func_return = self.repo.point_num_group_func(record)
        self.assertTrue('point_num' in func_return)
        self.assertTrue(len(func_return.keys()) == 1)

    def test_mapping_func(self):
        record = {
            "point_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": Mock(),
            "sum_hours_in_record": Mock()
        }

        func_return = self.repo.mapping_func(record)
        self.assertTrue('sum_value' in func_return)
        self.assertTrue('sum_hours_in_record' in func_return)

    def test_final_mapping_func(self):
        record = {
            'group': {
                'comparison_value': Mock(),
                'point_num': Mock()
            },
            'reduction': {
                'sum_value': Mock(),
                'year': Mock(),
                'sum_hours_in_record': Mock()
            }
        }

        func_return = self.repo.final_mapping_func(record)

        self.assertTrue(len(func_return.keys()) == 4)
        self.assertTrue('point_num' in func_return)
        self.assertTrue('comparison_value' in func_return)
        self.assertTrue('sum_value' in func_return)
        self.assertTrue('sum_hours_in_record' in func_return)

    def test_reduce_func(self):
        record_a = {
            "point_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": 1,
            "sum_hours_in_record": 1
        }
        record_b = {
            "point_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": 1,
            "sum_hours_in_record": 1
        }

        func_return = self.repo.reduce_func(record_a, record_b)

        self.assertTrue('sum_value' in func_return)
        self.assertTrue('sum_hours_in_record' in func_return)
        self.assertTrue(len(func_return.keys()) == 2)
        self.assertEqual(func_return['sum_value'], 2)
        self.assertEqual(func_return['sum_hours_in_record'], 2)

    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.syrx_group_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.syrx_map_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.syrx_reduce_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.syrx_final_map_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.format_syrx_data_for_kendo")
    def test_get_data_for_syrx_nums(self, format_syrx_data_for_kendo, syrx_final_map_func, syrx_reduce_func, syrx_map_func, syrx_group_func):
        syrx_nums = [Mock()]
        year = Mock()

        index_list = [[num, year, 'temp'] for num in syrx_nums]

        table_mock = self.uow.tables.compiled_equipment_point_records

        rv = self.repo.get_data_for_syrx_nums(syrx_nums, year, 1, 12)

        # table.get_all()
        table_mock.get_all.assert_called_with(*index_list, index='syrx_year')
        return_value = table_mock.get_all.return_value

        # table.get_all().filter()
        return_value = return_value.filter.return_value

        # table.get_all().group()
        return_value.group.assert_called_with(syrx_group_func)
        return_value = return_value.group.return_value

        # table.get_all().group().map()
        return_value.map.assert_called_with(syrx_map_func)
        return_value = return_value.map.return_value

        # table.get_all().group().map().reduce()
        return_value.reduce.assert_called_with(syrx_reduce_func)
        return_value = return_value.reduce.return_value

        # table.get_all().group().map().reduce().ungroup()
        return_value.ungroup.assert_called_with()
        return_value = return_value.ungroup.return_value

        # table.get_all().group().map().reduce().ungroup().map()
        return_value.map.assert_called_with(syrx_final_map_func)
        return_value = return_value.map.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        format_syrx_data_for_kendo.assert_called_with(return_value)
        return_value = format_syrx_data_for_kendo.return_value

        self.assertEqual(rv, return_value)

    def test_syrx_mapping_func(self):
        record = {
            "syrx_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": Mock(),
            "sum_hours_in_record": Mock()
        }

        func_return = self.repo.syrx_map_func(record)
        self.assertTrue('sum_value' in func_return)
        self.assertTrue('sum_hours_in_record' in func_return)

    def test_syrx_final_map_func(self):
        record = {
            'group': {
                'comparison_value': Mock()
            },
            'reduction': {
                'sum_value': Mock(),
                'year': Mock(),
                'sum_hours_in_record': Mock()
            }
        }

        func_return = self.repo.syrx_final_map_func(record)

        self.assertTrue(len(func_return.keys()) == 3)
        self.assertTrue('comparison_value' in func_return)
        self.assertTrue('sum_value' in func_return)
        self.assertTrue('sum_hours_in_record' in func_return)

    def test_syrx_reduce_func(self):
        record_a = {
            "syrx_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": 1,
            "sum_hours_in_record": 1
        }
        record_b = {
            "syrx_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": 1,
            "sum_hours_in_record": 1
        }

        func_return = self.repo.syrx_reduce_func(record_a, record_b)

        self.assertTrue('sum_value' in func_return)
        self.assertTrue('sum_hours_in_record' in func_return)
        self.assertTrue(len(func_return.keys()) == 2)
        self.assertEqual(func_return['sum_value'], 2)
        self.assertEqual(func_return['sum_hours_in_record'], 2)

    def test_syrx_group_func(self):
        record = {
            "syrx_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock()
        }

        func_return = self.repo.syrx_group_func(record)
        self.assertTrue('comparison_value' in func_return)
        self.assertTrue(len(func_return.keys()) == 1)

    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.summation_map_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.summation_reduce_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.default_func")
    def test_get_year_consumption_for_points(self, default_func, summation_reduce_func, summation_map_func):
        equipment_points = [
            {'syrx_num': Mock()},
            {'syrx_num': Mock()},
            {'syrx_num': Mock()}
        ]
        year = Mock()

        table_mock = self.uow.tables.compiled_equipment_point_records

        index_list = [
            [equipment_points[0]['syrx_num'], year, 'temp'],
            [equipment_points[1]['syrx_num'], year, 'temp'],
            [equipment_points[2]['syrx_num'], year, 'temp']
        ]

        rv = self.repo.get_year_consumption_data_for_points(equipment_points, year)

        # table.get_all()
        table_mock.get_all.assert_called_with(*index_list, index='syrx_year')
        return_value = table_mock.get_all.return_value

        # table.get_all().map()
        return_value.map.assert_called_with(summation_map_func)
        return_value = return_value.map.return_value

        # table.get_all().map().reduce()
        return_value.reduce.assert_called_with(summation_reduce_func)
        return_value = return_value.reduce.return_value

        # table.get_all().map().reduce().default()
        return_value.default.assert_called_with(default_func)
        return_value = return_value.default.return_value

        self.uow.run.assert_called_with(return_value)
        return_value = self.uow.run.return_value

        self.assertEqual(rv, return_value)

    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.summation_map_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.summation_reduce_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.default_func")
    def test_get_month_consumption_for_points(self, default_func, summation_reduce_func, summation_map_func):
        equipment_points = [
            {'syrx_num': Mock()},
            {'syrx_num': Mock()},
            {'syrx_num': Mock()}
        ]
        year = Mock()

        table_mock = self.uow.tables.compiled_equipment_point_records

        index_list = [
            [equipment_points[0]['syrx_num'], year, 'temp'],
            [equipment_points[1]['syrx_num'], year, 'temp'],
            [equipment_points[2]['syrx_num'], year, 'temp']
        ]

        rv = self.repo.get_month_consumption_data_for_points(equipment_points, year)

        # table.get_all()
        table_mock.get_all.assert_called_with(*index_list, index='syrx_year')
        return_value = table_mock.get_all.return_value

        # table.get_all().filter()
        return_value.filter.assert_called_with({'month':datetime.now().month})
        return_value = return_value.filter.return_value

        # table.get_all().filter().map()
        return_value.map.assert_called_with(summation_map_func)
        return_value = return_value.map.return_value

        # table.get_all().filter().map().reduce()
        return_value.reduce.assert_called_with(summation_reduce_func)
        return_value = return_value.reduce.return_value

        # table.get_all().filter().map().reduce().default()
        return_value.default.assert_called_with(default_func)
        return_value = return_value.default.return_value

        self.uow.run.assert_called_with(return_value)
        return_value = self.uow.run.return_value

        self.assertEqual(rv, return_value)

    def test_ppsn_map_func(self):
        record = {
            "point_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": 1,
            "sum_hours_in_record": 1
        }

        rv = self.repo.ppsn_map_func(record)

        self.assertTrue('sum_value' in rv)
        self.assertTrue('sum_hours_in_record' in rv)
        self.assertTrue(rv['sum_value'] == record['sum_value'])
        self.assertTrue(rv['sum_hours_in_record'] == record['sum_hours_in_record'])
        self.assertTrue(len(rv.keys()) == 2)

    def test_ppsn_reduce_func(self):
        record_a = {
            "point_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": 1,
            "sum_hours_in_record": 1
        }
        record_b = {
            "point_num": Mock(),
            "comparison_value": Mock(),
            "comparison_type": Mock(),
            "year": Mock(),
            "sum_value": 1,
            "sum_hours_in_record": 1
        }

        rv = self.repo.ppsn_reduce_func(record_a, record_b)

        self.assertTrue('sum_value' in rv)
        self.assertTrue('sum_hours_in_record' in rv)
        self.assertTrue('ppsn' not in rv)
        self.assertTrue(rv['sum_value'] == record_a['sum_value'] + record_b['sum_value'])
        self.assertTrue(rv['sum_hours_in_record'] == record_a['sum_hours_in_record'] + record_b['sum_hours_in_record'])
        self.assertTrue(len(rv.keys()) == 2)

    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.ppsn_map_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.ppsn_reduce_func")
    @patch("db.repositories.compiled_point_record_repository.CompiledPointRecordRepository.records_exist_for_get_all")
    def test_get_ppsn(self, records_exist_for_get_all, ppsn_reduce_func, ppsn_map_func,):
        point_nums = [Mock(), Mock(), Mock(), Mock()]
        report_year = Mock()

        table_mock = self.uow.tables.compiled_equipment_point_records
        records_exist_for_get_all.return_value = True

        self.uow.run.return_value = MagicMock()

        expected_index_list = [
            [point_nums[0], report_year, 'temp'],
            [point_nums[1], report_year, 'temp'],
            [point_nums[2], report_year, 'temp'],
            [point_nums[3], report_year, 'temp']
        ]

        rv = self.repo.get_ppsn(point_nums, report_year)

        records_exist_for_get_all.assert_called_with(expected_index_list, 'syrx_year')

        # table.get_all()
        table_mock.get_all.assert_called_with(*expected_index_list, index='syrx_year')
        return_value = table_mock.get_all.return_value

        # table.get_all().map()
        return_value.map.assert_called_with(ppsn_map_func)
        return_value = return_value.map.return_value

        # table.get_all().map().reduce()
        return_value.reduce.assert_called_with(ppsn_reduce_func)
        return_value = return_value.reduce.return_value

        self.uow.run.assert_called_with(return_value)

    def test_delete_for_syrx_num(self):
        syrx_num = Mock()
        table_mock = self.uow.tables.compiled_equipment_point_records

        self.repo.delete_for_syrx_num(syrx_num)

        # table.get_all()
        table_mock.get_all.assert_called_with(syrx_num, index='syrx_num')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)