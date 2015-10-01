import unittest
from db.repositories.unmapped_vendor_point_record_repository import UnmappedVendorPointRecordRepository
from mock import MagicMock, Mock

__author__ = 'badams'


class TestUnmappedVendorPointRecordRepository(unittest.TestCase):
    def setUp(self):
        self.uow = MagicMock()
        self.repo = UnmappedVendorPointRecordRepository(self.uow)

    def test_insert_insert_unmapped_vendor_point_records(self):
        records = [Mock(), Mock(), Mock()]
        table_mock = self.uow.tables.unmapped_vendor_point_records

        self.repo.insert_unmapped_vendor_point_records(records)

        # table.insert()
        table_mock.insert.assert_called_with(records)

        self.uow.run.assert_called_with(table_mock.insert.return_value)

    def test_get_all_vendor_points(self):
        table_mock = self.uow.tables.unmapped_vendor_point_records

        rv = self.repo.get_all_vendor_points()

        # table.pluck()
        table_mock.pluck.assert_called_with('vendor_point')
        return_value = table_mock.pluck.return_value

        # table.pluck().distinct()
        return_value.distinct.assert_called_with()
        return_value = return_value.distinct.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    def test_get_all_for_vendor_point_records_for_johnson(self):
        vendor_point = {'johnson_fqr': Mock(), 'johnson_site_id': Mock()}
        table_mock = self.uow.tables.unmapped_vendor_point_records

        rv = self.repo.get_all_vendor_point_records_for_johnson(vendor_point)

        # table.get_all()
        table_mock.get_all.assert_called_with([vendor_point['johnson_fqr'], vendor_point['johnson_site_id']], index='johnson')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    def test_get_all_vendor_point_records_for_fieldserver(self):
        vendor_point = {'fieldserver_offset': Mock(), 'fieldserver_site_id': Mock()}
        table_mock = self.uow.tables.unmapped_vendor_point_records

        rv = self.repo.get_all_vendor_point_records_for_fieldserver(vendor_point)

        # table.get_all()
        table_mock.get_all.assert_called_with([vendor_point['fieldserver_offset'], vendor_point['fieldserver_site_id']], index='fieldserver')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    def test_get_all_vendor_point_records_for_invensys(self):
        vendor_point = {'invensys_point_name': Mock(), 'invensys_equipment_name': Mock(), 'invensys_site_name': Mock()}
        table_mock = self.uow.tables.unmapped_vendor_point_records

        rv = self.repo.get_all_vendor_point_records_for_invensys(vendor_point)

        # table.get_all()
        table_mock.get_all.assert_called_with([vendor_point['invensys_point_name'], vendor_point['invensys_equipment_name'], vendor_point['invensys_site_name']], index='invensys')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    def test_get_all_vendor_point_records_for_siemens(self):
        vendor_point = {'siemens_meter_name': Mock()}
        table_mock = self.uow.tables.unmapped_vendor_point_records

        rv = self.repo.get_all_vendor_point_records_for_siemens(vendor_point)

        # table.get_all()
        table_mock.get_all.assert_called_with([vendor_point['siemens_meter_name']], index='siemens')
        return_value = table_mock.get_all.return_value

        self.uow.run_list.assert_called_with(return_value)
        return_value = self.uow.run_list.return_value

        self.assertEqual(rv, return_value)

    def test_delete_all_for_johnson_point(self):
        vendor_point = {'johnson_fqr': Mock(),
                        'johnson_site_id': Mock()}
        table_mock = self.uow.tables.unmapped_vendor_point_records

        self.repo.delete_all_for_johnson_point(vendor_point)

        # table.get_all()
        table_mock.get_all.assert_called_with([vendor_point['johnson_fqr'], vendor_point['johnson_site_id']], index='johnson')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)

    def test_delete_all_for_fieldserver_point(self):
        vendor_point = {'fieldserver_offset': Mock(),
                        'fieldserver_site_id': Mock()}
        table_mock = self.uow.tables.unmapped_vendor_point_records

        self.repo.delete_all_for_fieldserver_point(vendor_point)

        # table.get_all()
        table_mock.get_all.assert_called_with([vendor_point['fieldserver_offset'], vendor_point['fieldserver_site_id']], index='fieldserver')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)

    def test_delete_all_for_invensys_point(self):
        vendor_point = {'invensys_point_name': Mock(),
                        'invensys_equipment_name': Mock(),
                        'invensys_site_name': Mock()}
        table_mock = self.uow.tables.unmapped_vendor_point_records

        self.repo.delete_all_for_invensys_point(vendor_point)

        # table.get_all()
        table_mock.get_all.assert_called_with([vendor_point['invensys_point_name'], vendor_point['invensys_equipment_name'], vendor_point['invensys_site_name']], index='invensys')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)

    def test_delete_all_for_siemens_point(self):
        vendor_point = {'siemens_meter_name': Mock()}
        table_mock = self.uow.tables.unmapped_vendor_point_records

        self.repo.delete_all_for_siemens_point(vendor_point)

        # table.get_all()
        table_mock.get_all.assert_called_with([vendor_point['siemens_meter_name']], index='siemens')
        return_value = table_mock.get_all.return_value

        # table.get_all().delete()
        return_value.delete.assert_called_with()
        return_value = return_value.delete.return_value

        self.uow.run.assert_called_with(return_value)