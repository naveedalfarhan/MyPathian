import datetime
import unittest
import dateutil.parser
from mock import Mock, patch, call
import pytz
from vendor_data_pipeline.global_vendor_point_handler import GlobalVendorPointHandler

__author__ = 'badams'


class TestGlobalVendorPointHandler(unittest.TestCase):
    @patch("vendor_data_pipeline.global_vendor_point_handler.UoW")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._process_global_vendor_point")
    def test_process_all_global_vendor_points(self, _process_global_vendor_point, uow):
        global_vendor_point_handler = GlobalVendorPointHandler()
        global_vendor_point_handler.logger = Mock()
        ret_val = [{'johnson_fqr': Mock(), 'johnson_site_id': Mock(), 'source': 'johnson'},
                   {'fieldserver_offset': Mock(), 'fieldserver_site_id': Mock(), 'source': 'fieldserver'},
                   {'siemens_meter_name': Mock(), 'source': 'siemens'},
                   {'invensys_site_name': Mock(), 'invensys_equipment_name': Mock(),
                    'invensys_point_name': Mock(), 'source': 'invensys'}]
        uow.return_value.data_mapping.get_all_global_vendor_points.return_value = ret_val

        global_vendor_point_handler.process_all_global_vendor_points()

        uow.return_value.data_mapping.get_all_global_vendor_points.assert_called_with()

        _process_global_vendor_point.assert_has_calls([call(ret_val[0]),
                                                       call(ret_val[1]),
                                                       call(ret_val[2]),
                                                       call(ret_val[3])])

    @patch("vendor_data_pipeline.global_vendor_point_handler.UoW")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._handle_mapping")
    def test_process_global_vendor_point(self, _handle_mapping, uow):
        global_vendor_point_handler = GlobalVendorPointHandler()
        global_vendor_point_handler.logger = Mock()
        johnson_fqr = Mock()
        johnson_site_id = Mock()
        ret_val = [{'syrx_num': Mock(), 'johnson_fqr': johnson_fqr,
                    'johnson_site_id': johnson_site_id, 'source': 'johnson'},
                   {'syrx_num': Mock(), 'johnson_fqr': johnson_fqr,
                    'johnson_site_id': johnson_site_id, 'source': 'johnson'},
                   {'syrx_num': Mock(), 'johnson_fqr': johnson_fqr,
                    'johnson_site_id': johnson_site_id, 'source': 'johnson'}]

        gvp = {'johnson_fqr': johnson_fqr,
               'johnson_site_id': johnson_site_id,
               'source': 'johnson'}

        uow.return_value.data_mapping.get_mappings_for_johnson_site_id_fqr.return_value = ret_val

        global_vendor_point_handler._process_global_vendor_point(gvp)

        uow.return_value.data_mapping.get_mappings_for_johnson_site_id_fqr.assert_called_with([[gvp['johnson_site_id'],
                                                                                                gvp['johnson_fqr']]])
        _handle_mapping.assert_has_calls([call(ret_val[0]),
                                          call(ret_val[1]),
                                          call(ret_val[2])])

    @patch("vendor_data_pipeline.global_vendor_point_handler.UoW")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._get_existing_records_by_datetime")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._find_new_records")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._insert_new_records")
    def test_handle_mapping(self, _insert_new_records, _find_new_records, _get_existing_records_by_datetime, uow):
        global_vendor_point_handler = GlobalVendorPointHandler()
        global_vendor_point_handler.logger = Mock()
        mapping = {'syrx_num': Mock(), 'johnson_fqr': Mock(),
                   'johnson_site_id': Mock(), 'source': 'johnson'}

        global_vendor_point_handler._handle_mapping(mapping)

        uow.return_value.energy_records.get_all_equipment_point_records_for_syrx_num.assert_called_with(mapping['syrx_num'])

        _get_existing_records_by_datetime.assert_called_with(uow.return_value.energy_records.get_all_equipment_point_records_for_syrx_num.return_value)
        _find_new_records.assert_called_with(mapping, _get_existing_records_by_datetime.return_value)
        _insert_new_records.assert_called_with(mapping, _find_new_records.return_value)

    @patch("vendor_data_pipeline.global_vendor_point_handler.UoW")
    def test_get_existing_records_by_datetime(self, uow):
        global_vendor_point_handler = GlobalVendorPointHandler()
        global_vendor_point_handler.logger = Mock()
        records = [{'date': Mock(), 'value': 1},
                   {'date': Mock(), 'value': 2},
                   {'date': Mock(), 'value': 3}]

        rv = global_vendor_point_handler._get_existing_records_by_datetime(records)

        self.assertEqual(len(rv.keys()), 3)
        self.assertTrue(records[0]['date'] in rv.keys() and records[1]['date'] in rv.keys() and
                        records[2]['date'] in rv.keys())

    @patch("vendor_data_pipeline.global_vendor_point_handler.UoW")
    def test_get_all_records_by_datetime(self, uow):
        global_vendor_point_handler = GlobalVendorPointHandler()
        global_vendor_point_handler.logger = Mock()
        records = [{'date': Mock(), 'value': 1},
                   {'date': Mock(), 'value': 2}]

        rv = global_vendor_point_handler._get_all_records_by_datetime(records)

        self.assertEqual(len(rv.keys()), 2)
        self.assertTrue(records[0]['date'] in rv.keys() and records[1]['date'] in rv.keys())

    @patch("vendor_data_pipeline.global_vendor_point_handler.UoW")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._get_all_records_by_datetime")
    def test_find_new_records(self, _get_all_records_by_datetime, uow):
        global_vendor_point_handler = GlobalVendorPointHandler()
        global_vendor_point_handler.logger = Mock()
        mapping = {'syrx_num': Mock(), 'johnson_fqr': Mock(),
                   'johnson_site_id': Mock(), 'source': 'johnson'}
        date_1_mock = Mock()
        date_2_mock = Mock()
        date_3_mock = Mock()
        date_4_mock = Mock()
        existing_records = {date_1_mock: {'date': date_1_mock, 'value': 1},
                            date_2_mock: {'date': date_2_mock, 'value': 2}}
        all_records = [{'date': date_1_mock, 'value': 1},
                       {'date': date_2_mock, 'value': 2},
                       {'date': date_3_mock, 'value': 3},
                       {'date': date_4_mock, 'value': 4}]
        all_records_by_date = {date_1_mock: all_records[0],
                               date_2_mock: all_records[1],
                               date_3_mock: all_records[2],
                               date_4_mock: all_records[3]}
        uow.return_value.global_vendor_point_records.get_all_for_johnson_point.return_value = all_records
        _get_all_records_by_datetime.return_value = all_records_by_date

        rv = global_vendor_point_handler._find_new_records(mapping, existing_records)

        uow.return_value.global_vendor_point_records.get_all_for_johnson_point.assert_called_with(mapping['johnson_site_id'],
                                                                                                  mapping['johnson_fqr'])
        _get_all_records_by_datetime.assert_called_with(all_records)

        self.assertEqual(len(rv), 2)
        self.assertTrue(all_records[2] in rv)
        self.assertTrue(all_records[3] in rv)

    @patch("vendor_data_pipeline.global_vendor_point_handler.UoW")
    @patch("vendor_data_pipeline.global_vendor_point_handler.EnergyRecordCompiler")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._populate_weatherstation_id_on_records")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._get_weather_data")
    @patch("vendor_data_pipeline.global_vendor_point_handler.GlobalVendorPointHandler._handle_bad_records")
    def test_insert_new_records(self, _handle_bad_records, _get_weather_data, _populate_weatherstation_id_on_records, energy_record_compiler, uow):
        global_vendor_point_handler = GlobalVendorPointHandler()
        global_vendor_point_handler.logger = Mock()

        date_1 = datetime.datetime(2014, 1, 1)
        date_2 = datetime.datetime(2014, 1, 2)
        date_1_utc = pytz.utc.localize(date_1)
        date_2_utc = pytz.utc.localize(date_2)
        mapping = {'syrx_num': Mock(), 'johnson_fqr': Mock(),
                   'johnson_site_id': Mock(), 'source': 'johnson'}
        records_to_insert = [{'date': date_1_utc, 'value': 3, 'timestamp': '2014-01-01 00:00:00'},
                             {'date': date_2_utc, 'value': 4, 'timestamp': '2014-01-02 00:00:00'}]
        weather_data = {'1': {date_1_utc: Mock(),
                              date_2_utc: Mock()}}
        _get_weather_data.return_value = weather_data

        def populate_weatherstation_id_side_effect(syrx_num, records):
            for r in records:
                r['weatherstation_id'] = '1'
        _populate_weatherstation_id_on_records.side_effect = populate_weatherstation_id_side_effect

        def get_equipment_point_record_side_effect(dt, syrx, value, weather, dt_2):
            return {'date': '1'}
        uow.return_value.energy_records.get_equipment_point_record.side_effect = get_equipment_point_record_side_effect

        global_vendor_point_handler._insert_new_records(mapping, records_to_insert)

        _populate_weatherstation_id_on_records.assert_called_with(mapping['syrx_num'], records_to_insert)
        _get_weather_data.assert_called_with(records_to_insert)

        uow.return_value.energy_records.get_equipment_point_record.assert_any_call(date_1_utc,
                                                                                   mapping['syrx_num'],
                                                                                   float(records_to_insert[0]['value']),
                                                                                   weather_data['1'][date_1_utc],
                                                                                   global_vendor_point_handler.date_time)
        uow.return_value.energy_records.get_equipment_point_record.assert_any_call(date_2_utc,
                                                                                   mapping['syrx_num'],
                                                                                   float(records_to_insert[1]['value']),
                                                                                   weather_data['1'][date_2_utc],
                                                                                   global_vendor_point_handler.date_time)

        uow.return_value.energy_records.insert_equipment_point_records.assert_called_with([{'date': '1'}, {'date': '1'}])

        self.assertTrue(not _handle_bad_records.called)