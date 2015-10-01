import unittest
from db.repositories.global_vendor_point_record_repository import GlobalVendorPointRecordRepository
from mock import MagicMock, Mock, patch

__author__ = 'Brian'


class TestGlobalVendorPointRecordRepository(unittest.TestCase):
    def setUp(self):
        self.uow = MagicMock()
        self.repo = GlobalVendorPointRecordRepository(self.uow)

    def test_insert_global_vendor_point_records(self):
        records = [Mock(), Mock(), Mock()]
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.insert_global_vendor_point_records(records)

        # table.insert()
        table_mock.insert.assert_called_with(records)
        return_value = table_mock.insert.return_value

        self.uow.run.assert_called_with(return_value)

    def test_get_all_for_johnson_point(self):
        johnson_site_id = Mock()
        johnson_fqr = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.get_all_for_johnson_point(johnson_site_id, johnson_fqr)

        # table.get_all()
        table_mock.get_all.assert_called_with([johnson_site_id, johnson_fqr], index='johnson')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)

    def test_get_all_for_fieldserver(self):
        fieldserver_site_id = Mock()
        fieldserver_offset = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.get_all_for_fieldserver_point(fieldserver_site_id, fieldserver_offset)

        # table.get_all()
        table_mock.get_all.assert_called_with([fieldserver_site_id, fieldserver_offset], index='fieldserver')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)

    def test_get_all_for_invensys_point(self):
        invensys_site_name = Mock()
        invensys_equipment_name = Mock()
        invensys_meter_name = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.get_all_for_invensys_point(invensys_site_name, invensys_equipment_name, invensys_meter_name)

        # table,get_all
        table_mock.get_all.assert_called_with([invensys_site_name, invensys_equipment_name, invensys_meter_name],
                                              index='invensys')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)

    def test_get_all_for_siemens_point(self):
        siemens_meter_name = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.get_all_for_siemens_point(siemens_meter_name)

        # table.get_all()
        table_mock.get_all.assert_called_with([siemens_meter_name], index='siemens')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)

    def test_date_map_func(self):
        record = {'date': '1', 'Test': 1}

        rv = self.repo.date_map_func(record)

        self.assertEqual('1', rv)

    @patch("db.repositories.global_vendor_point_record_repository.GlobalVendorPointRecordRepository.date_map_func")
    def test_get_existing_dates_for_johnson(self, date_map_func):
        site_id = Mock()
        fqr = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        rv = self.repo.get_existing_dates_for_johnson(site_id, fqr)

        # table.get_all()
        table_mock.get_all.assert_called_with([site_id, fqr], index='johnson')
        return_value = table_mock.get_all.return_value

        # table.get_all().map()
        return_value.map.assert_called_with(date_map_func)
        return_value = return_value.map.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    @patch("db.repositories.global_vendor_point_record_repository.GlobalVendorPointRecordRepository.date_map_func")
    def test_get_existing_dates_for_fieldserver(self, date_map_func):
        site_id = Mock()
        offset = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        rv = self.repo.get_existing_dates_for_fieldserver(site_id, offset)

        # table.get_all()
        table_mock.get_all.assert_called_with([site_id, offset], index='fieldserver')
        return_value = table_mock.get_all.return_value

        # table.get_all().map()
        return_value.map.assert_called_with(date_map_func)
        return_value = return_value.map.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    @patch("db.repositories.global_vendor_point_record_repository.GlobalVendorPointRecordRepository.date_map_func")
    def test_get_existing_dates_for_invensys(self, date_map_func):
        site_name = Mock()
        equipment_name = Mock()
        point_name = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        rv = self.repo.get_existing_dates_for_invensys(site_name, equipment_name, point_name)

        # table.get_all()
        table_mock.get_all.assert_called_with([site_name, equipment_name, point_name], index='invensys')
        return_value = table_mock.get_all.return_value

        # table.get_all().map()
        return_value.map.assert_called_with(date_map_func)
        return_value = return_value.map.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(return_value, rv)

    @patch("db.repositories.global_vendor_point_record_repository.GlobalVendorPointRecordRepository.date_map_func")
    def test_get_existing_dates_for_siemens(self, date_map_func):
        siemens_meter_name = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        rv = self.repo.get_existing_dates_for_siemens(siemens_meter_name)

        # table.get_all()
        table_mock.get_all.assert_called_with([siemens_meter_name], index='siemens')
        return_value = table_mock.get_all.return_value

        # table.get_all().map()
        return_value.map.assert_called_with(date_map_func)
        return_value = return_value.map.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(return_value, rv)

    def test_delete_all_for_johnson_point(self):
        site_id = Mock()
        fqr = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.delete_all_for_johnson_point(site_id, fqr)

        # table.get_all()
        table_mock.get_all.assert_called_with([site_id, fqr], index='johnson')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)

    def test_delete_all_for_fieldserver_point(self):
        site_id = Mock()
        offset = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.delete_all_for_fieldserver_point(site_id, offset)

        # table.get_all()
        table_mock.get_all.assert_called_with([site_id, offset], index='fieldserver')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)

    def test_delete_all_for_invensys_point(self):
        site_name = Mock()
        equip_name = Mock()
        point_name = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.delete_all_for_invensys_point(site_name, equip_name, point_name)

        # table.get_all()
        table_mock.get_all.assert_called_with([site_name, equip_name, point_name], index='invensys')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)

    def test_delete_all_for_siemens_point(self):
        meter_name = Mock()
        table_mock = self.uow.tables.global_vendor_point_records

        self.repo.delete_all_for_siemens_point(meter_name)

        # table.get_all()
        table_mock.get_all.assert_called_with([meter_name], index='siemens')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)