from datetime import datetime
import unittest
from mock import MagicMock, patch, call, Mock
from nightly_process.unmapped_syrx_num_handler import UnmappedSyrxNumHandler

__author__ = 'badams'


class TestUnmappedSyrxNumHandler(unittest.TestCase):
    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._get_unmapped_syrx_nums")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._move_data_for_syrx_nums")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._delete_noncompiled_records_for_syrx_nums")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._delete_compiled_records_for_syrx_nums")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._move_data_to_new_mappings")
    def test_run(self, _move_data_to_new_mappings, _delete_compiled_records_for_syrx_nums, _delete_noncompiled_records_for_syrx_nums, _move_data_for_syrx_nums, _get_unmapped_syrx_nums, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        unmapped_syrx_num_handler.logger = MagicMock()
        unmapped_syrx_num_handler.run()

        _get_unmapped_syrx_nums.assert_called_with()
        _move_data_for_syrx_nums.assert_called_with()
        _delete_noncompiled_records_for_syrx_nums.assert_called_with()
        _delete_compiled_records_for_syrx_nums.assert_called_with()
        _move_data_to_new_mappings.assert_called_with()

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    def test_get_unmapped_syrx_nums(self, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()

        unmapped_syrx_num_handler._get_unmapped_syrx_nums()

        uow_mock.return_value.unmapped_syrx_nums.get_all.assert_called_with()

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._move_data_for_syrx_num")
    def test_move_data_for_syrx_nums(self, _move_data_for_syrx_num, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        syrx_num_list = [{'syrx_num': 1,
                          'vendor_point': {'source': 'Test'}},
                         {'syrx_num': 2,
                          'vendor_point': {'source': 'Test2'}},
                         {'syrx_num': 3,
                          'vendor_point': {'source': 'Test3'}}]
        unmapped_syrx_num_handler.unmapped_syrx_nums = syrx_num_list

        unmapped_syrx_num_handler._move_data_for_syrx_nums()

        _move_data_for_syrx_num.assert_has_calls([call(syrx_num_list[0]),
                                                  call(syrx_num_list[1]),
                                                  call(syrx_num_list[2])])

        uow_mock.return_value.unmapped_syrx_nums.remove_syrx_num.assert_has_calls([call(syrx_num_list[0]['syrx_num']),
                                                                                           call(syrx_num_list[1]['syrx_num']),
                                                                                           call(syrx_num_list[2]['syrx_num'])
        ])

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._handle_unmapping_records_for_syrx_num")
    def test_move_data_for_syrx_num_non_global(self, _handle_unmapping_records_for_syrx_num, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        unmapped_syrx_num = {'syrx_num': '1',
                             'vendor_point': {'source': 'Test'}}
        records_list = Mock()
        uow_mock.return_value.equipment.get_data_for_syrx_num.return_value = records_list

        unmapped_syrx_num_handler._move_data_for_syrx_num(unmapped_syrx_num)

        uow_mock.return_value.equipment.get_data_for_syrx_num.assert_called_with(unmapped_syrx_num['syrx_num'])
        _handle_unmapping_records_for_syrx_num.assert_called_with(unmapped_syrx_num, records_list)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._handle_unmapping_records_for_global_vendor_point")
    def test_move_data_for_syrx_num_global_johnson(self, _handle_unmapping, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        unmapped_syrx_num = {'syrx_num': '1',
                             'vendor_point': {'source': 'johnson',
                                              'johnson_site_id': '1',
                                              'johnson_fqr': '1'}}

        records_list = [1,2]
        uow_mock.return_value.global_vendor_point_records.get_all_for_johnson_point.return_value = records_list

        unmapped_syrx_num_handler._move_data_for_syrx_num(unmapped_syrx_num)

        uow_mock.return_value.global_vendor_point_records.get_all_for_johnson_point.assert_called_with(unmapped_syrx_num['vendor_point']['johnson_site_id'],
                                                                                                       unmapped_syrx_num['vendor_point']['johnson_fqr'])

        _handle_unmapping.assert_called_with(unmapped_syrx_num, records_list)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._handle_unmapping_records_for_global_vendor_point")
    def test_move_data_for_syrx_num_global_fieldserver(self, _handle_unmapping, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        unmapped_syrx_num = {'syrx_num': '1',
                             'vendor_point': {'source': 'fieldserver',
                                              'fieldserver_site_id': '1',
                                              'fieldserver_offset': '1'}}

        records_list = [1,2]
        uow_mock.return_value.global_vendor_point_records.get_all_for_fieldserver_point.return_value = records_list

        unmapped_syrx_num_handler._move_data_for_syrx_num(unmapped_syrx_num)

        uow_mock.return_value.global_vendor_point_records.get_all_for_fieldserver_point.assert_called_with(unmapped_syrx_num['vendor_point']['fieldserver_site_id'],
                                                                                                           unmapped_syrx_num['vendor_point']['fieldserver_offset'])

        _handle_unmapping.assert_called_with(unmapped_syrx_num, records_list)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._handle_unmapping_records_for_global_vendor_point")
    def test_move_data_for_syrx_num_global_invensys(self, _handle_unmapping, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        unmapped_syrx_num = {'syrx_num': '1',
                             'vendor_point': {'source': 'invensys',
                                              'invensys_site_name': '1',
                                              'invensys_equipment_name': '1',
                                              'invensys_point_name': '1'}}

        records_list = [1,2]
        uow_mock.return_value.global_vendor_point_records.get_all_for_invensys_point.return_value = records_list

        unmapped_syrx_num_handler._move_data_for_syrx_num(unmapped_syrx_num)

        uow_mock.return_value.global_vendor_point_records.get_all_for_invensys_point.assert_called_with(unmapped_syrx_num['vendor_point']['invensys_site_name'],
                                                                                                        unmapped_syrx_num['vendor_point']['invensys_equipment_name'],
                                                                                                        unmapped_syrx_num['vendor_point']['invensys_point_name'])

        _handle_unmapping.assert_called_with(unmapped_syrx_num, records_list)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._handle_unmapping_records_for_global_vendor_point")
    def test_move_data_for_syrx_num_global_siemens(self, _handle_unmapping, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        unmapped_syrx_num = {'syrx_num': '1',
                             'vendor_point': {'source': 'siemens',
                                              'siemens_meter_name': '1'}}

        records_list = [1,2]
        uow_mock.return_value.global_vendor_point_records.get_all_for_siemens_point.return_value = records_list

        unmapped_syrx_num_handler._move_data_for_syrx_num(unmapped_syrx_num)

        uow_mock.return_value.global_vendor_point_records.get_all_for_siemens_point.assert_called_with(unmapped_syrx_num['vendor_point']['siemens_meter_name'])

        _handle_unmapping.assert_called_with(unmapped_syrx_num, records_list)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    def test_handle_unmapping_records_for_syrx_num(self, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        syrx_num = {'syrx_num': '1',
                    'vendor_point': {'source': 'Test'}}
        records_list = [{'value': 1,
                         'syrx_num': '1',
                         'weather': MagicMock(),
                         'id': '1',
                         'created_on': MagicMock(),
                         'source': 'Test'},
                        {'value': 2,
                         'syrx_num': '1',
                         'weather': MagicMock(),
                         'id': '2',
                         'created_on': MagicMock(),
                         'source': 'Test'},
                        {'value': 3,
                         'syrx_num': '1',
                         'weather': MagicMock(),
                         'id': '3',
                         'created_on': MagicMock(),
                         'source': 'Test'}]
        final_list = [{'value': 1,
                       'weather': records_list[0]['weather'],
                       'created_on': records_list[0]['created_on'],
                       'source': 'Test'},
                      {'value': 2,
                       'weather': records_list[1]['weather'],
                       'created_on': records_list[1]['created_on'],
                       'source': 'Test'},
                      {'value': 3,
                       'weather': records_list[2]['weather'],
                       'created_on': records_list[2]['created_on'],
                       'source': 'Test'}]

        unmapped_syrx_num_handler._handle_unmapping_records_for_syrx_num(syrx_num, records_list)

        uow_mock.return_value.unmapped_vendor_point_records.insert_unmapped_vendor_point_records.assert_called_with(final_list)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    def test_delete_noncompiled_records_for_syrx_nums(self, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        syrx_nums = [{'syrx_num': '1'},
                     {'syrx_num': '2'},
                     {'syrx_num': '3'}]
        unmapped_syrx_num_handler.unmapped_syrx_nums = syrx_nums

        unmapped_syrx_num_handler._delete_noncompiled_records_for_syrx_nums()

        uow_mock.return_value.energy_records.delete_for_syrx_num.assert_has_calls([call('1'),
                                                                                   call('2'),
                                                                                   call('3')])

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    def test_delete_compiled_records_for_syrx_nums(self, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        syrx_nums = [{'syrx_num': '1'},
                     {'syrx_num': '2'},
                     {'syrx_num': '3'}]
        unmapped_syrx_num_handler.unmapped_syrx_nums = syrx_nums

        unmapped_syrx_num_handler._delete_compiled_records_for_syrx_nums()

        uow_mock.return_value.compiled_point_records.delete_for_syrx_num.assert_has_calls([call('1'),
                                                                                                   call('2'),
                                                                                                   call('3')])

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._move_unknown_data_for_johnson")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._move_unknown_data_for_fieldserver")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._move_unknown_data_for_invensys")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._move_unknown_data_for_siemens")
    def test_move_data_to_new_mappings(self, _move_unknown_data_for_siemens, _move_unknown_data_for_invensys, _move_unknown_data_for_fieldserver, _move_unknown_data_for_johnson, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        unmapped_syrx_num_handler.logger = MagicMock()

        unmapped_syrx_num_handler._move_data_to_new_mappings()

        _move_unknown_data_for_johnson.assert_called_with()
        _move_unknown_data_for_fieldserver.assert_called_with()
        _move_unknown_data_for_invensys.assert_called_with()
        _move_unknown_data_for_siemens.assert_called_with()

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._add_data_for_mapping")
    def test_move_unknown_data_for_johnson(self, _add_data_for_mapping, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        data_mapping_records = [{'source': 'johnson',
                                 'johnson_fqr': Mock(),
                                 'johnson_site_id': Mock(),
                                 'syrx_num': Mock()},
                                {'source': 'johnson',
                                 'johnson_fqr': Mock(),
                                 'johnson_site_id': Mock(),
                                 'syrx_num': Mock()},
                                {'source': 'johnson',
                                 'johnson_fqr': Mock(),
                                 'johnson_site_id': Mock(),
                                 'syrx_num': Mock()}]

        call_list = [{'johnson_fqr': data_mapping_records[0]['johnson_fqr'],
                      'johnson_site_id': data_mapping_records[0]['johnson_site_id'],
                      'source': 'johnson'},
                     {'johnson_fqr': data_mapping_records[1]['johnson_fqr'],
                      'johnson_site_id': data_mapping_records[1]['johnson_site_id'],
                      'source': 'johnson'},
                     {'johnson_fqr': data_mapping_records[2]['johnson_fqr'],
                      'johnson_site_id': data_mapping_records[2]['johnson_site_id'],
                      'source': 'johnson'}]

        uow_mock.return_value.data_mapping.get_all_mappings_for_johnson.return_value = data_mapping_records

        unmapped_syrx_num_handler._move_unknown_data_for_johnson()

        uow_mock.return_value.data_mapping.get_all_mappings_for_johnson.assert_called_with()\

        _add_data_for_mapping.assert_has_calls([call(call_list[0], data_mapping_records[0]['syrx_num']),
                                                call(call_list[1], data_mapping_records[1]['syrx_num']),
                                                call(call_list[2], data_mapping_records[2]['syrx_num'])])

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._add_data_for_mapping")
    def test_move_unknown_data_for_fieldserver(self, _add_data_for_mapping, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        data_mapping_records = [{'source': 'fieldserver',
                                 'fieldserver_offset': Mock(),
                                 'fieldserver_site_id': Mock(),
                                 'syrx_num': Mock()},
                                {'source': 'fieldserver',
                                 'fieldserver_offset': Mock(),
                                 'fieldserver_site_id': Mock(),
                                 'syrx_num': Mock()},
                                {'source': 'fieldserver',
                                 'fieldserver_offset': Mock(),
                                 'fieldserver_site_id': Mock(),
                                 'syrx_num': Mock()}]

        call_list = [{'fieldserver_offset': data_mapping_records[0]['fieldserver_offset'],
                      'fieldserver_site_id': data_mapping_records[0]['fieldserver_site_id'],
                      'source': 'fieldserver'},
                     {'fieldserver_offset': data_mapping_records[1]['fieldserver_offset'],
                      'fieldserver_site_id': data_mapping_records[1]['fieldserver_site_id'],
                      'source': 'fieldserver'},
                     {'fieldserver_offset': data_mapping_records[2]['fieldserver_offset'],
                      'fieldserver_site_id': data_mapping_records[2]['fieldserver_site_id'],
                      'source': 'fieldserver'}]

        uow_mock.return_value.data_mapping.get_all_mappings_for_fieldserver.return_value = data_mapping_records

        unmapped_syrx_num_handler._move_unknown_data_for_fieldserver()

        uow_mock.return_value.data_mapping.get_all_mappings_for_fieldserver.assert_called_with()

        _add_data_for_mapping.assert_has_calls([call(call_list[0], data_mapping_records[0]['syrx_num']),
                                                call(call_list[1], data_mapping_records[1]['syrx_num']),
                                                call(call_list[2], data_mapping_records[2]['syrx_num'])])

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._add_data_for_mapping")
    def test_move_unknown_data_for_invensys(self, _add_data_for_mapping, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        data_mapping_records = [{'source': 'invensys',
                                 'invensys_point_name': Mock(),
                                 'invensys_site_name': Mock(),
                                 'invensys_equipment_name': Mock(),
                                 'syrx_num': Mock()},
                                {'source': 'invensys',
                                 'invensys_point_name': Mock(),
                                 'invensys_site_name': Mock(),
                                 'invensys_equipment_name': Mock(),
                                 'syrx_num': Mock()},
                                {'source': 'invensys',
                                 'invensys_point_name': Mock(),
                                 'invensys_site_name': Mock(),
                                 'invensys_equipment_name': Mock(),
                                 'syrx_num': Mock()}]

        call_list = [{'invensys_point_name': data_mapping_records[0]['invensys_point_name'],
                      'invensys_site_name': data_mapping_records[0]['invensys_site_name'],
                      'invensys_equipment_name': data_mapping_records[0]['invensys_equipment_name'],
                      'source': 'invensys'},
                     {'invensys_point_name': data_mapping_records[1]['invensys_point_name'],
                      'invensys_site_name': data_mapping_records[1]['invensys_site_name'],
                      'invensys_equipment_name': data_mapping_records[1]['invensys_equipment_name'],
                      'source': 'invensys'},
                     {'invensys_point_name': data_mapping_records[2]['invensys_point_name'],
                      'invensys_site_name': data_mapping_records[2]['invensys_site_name'],
                      'invensys_equipment_name': data_mapping_records[2]['invensys_equipment_name'],
                      'source': 'invensys'}]

        uow_mock.return_value.data_mapping.get_all_mappings_for_invensys.return_value = data_mapping_records

        unmapped_syrx_num_handler._move_unknown_data_for_invensys()

        uow_mock.return_value.data_mapping.get_all_mappings_for_invensys.assert_called_with()

        _add_data_for_mapping.assert_has_calls([call(call_list[0], data_mapping_records[0]['syrx_num']),
                                                call(call_list[1], data_mapping_records[1]['syrx_num']),
                                                call(call_list[2], data_mapping_records[2]['syrx_num'])])

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.UnmappedSyrxNumHandler._add_data_for_mapping")
    def test_move_unknown_data_for_siemens(self, _add_data_for_mapping, uow_mock):
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        data_mapping_records = [{'source': 'siemens',
                                 'siemens_meter_name': Mock(),
                                 'syrx_num': Mock()},
                                {'source': 'siemens',
                                 'siemens_meter_name': Mock(),
                                 'syrx_num': Mock()},
                                {'source': 'siemens',
                                 'siemens_meter_name': Mock(),
                                 'syrx_num': Mock()}]

        call_list = [{'siemens_meter_name': data_mapping_records[0]['siemens_meter_name'],
                      'source': 'siemens'},
                     {'siemens_meter_name': data_mapping_records[1]['siemens_meter_name'],
                      'source': 'siemens'},
                     {'siemens_meter_name': data_mapping_records[2]['siemens_meter_name'],
                      'source': 'siemens'}]

        uow_mock.return_value.data_mapping.get_all_mappings_for_siemens.return_value = data_mapping_records

        unmapped_syrx_num_handler._move_unknown_data_for_siemens()

        uow_mock.return_value.data_mapping.get_all_mappings_for_siemens.assert_called_with()

        _add_data_for_mapping.assert_has_calls([call(call_list[0], data_mapping_records[0]['syrx_num']),
                                                call(call_list[1], data_mapping_records[1]['syrx_num']),
                                                call(call_list[2], data_mapping_records[2]['syrx_num'])])

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.EnergyRecordCompiler")
    def test_add_data_for_mapping_johnson(self, energy_record_compiler, uow_mock):
        data_mapping = {'johnson_fqr': Mock(),
                        'johnson_site_id': Mock(),
                        'source': 'johnson'}
        first_datetime = datetime(1,1,1)
        second_datetime = datetime(1,1,2)
        unknown_vendor_point_records = [{'value': 1,
                                         'id': Mock(),
                                         'created_on': Mock(),
                                         'weather': Mock(),
                                         'date': first_datetime,
                                         'johnson_fqr': data_mapping['johnson_fqr'],
                                         'johnson_site_id': data_mapping['johnson_site_id'],
                                         'source': 'johnson'
                                         },
                                        {'value': 2,
                                         'id': Mock(),
                                         'created_on': Mock(),
                                         'weather': Mock(),
                                         'date': second_datetime,
                                         'johnson_fqr': data_mapping['johnson_fqr'],
                                         'johnson_site_id': data_mapping['johnson_site_id'],
                                         'source': 'johnson'
                                         }]
        insert_list = [{'value': 1,
                        'syrx_num': '1',
                        'weather': unknown_vendor_point_records[0]['weather'],
                        'created_on': unknown_vendor_point_records[0]['created_on'],
                        'date': first_datetime},
                       {'value': 2,
                        'syrx_num': '1',
                        'weather': unknown_vendor_point_records[1]['weather'],
                        'created_on': unknown_vendor_point_records[1]['created_on'],
                        'date': second_datetime}]
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        uow_mock.return_value.unmapped_vendor_point_records.get_all_vendor_point_records_for_johnson.return_value = unknown_vendor_point_records

        unmapped_syrx_num_handler._add_data_for_mapping(data_mapping, '1')

        uow_mock.return_value.unmapped_vendor_point_records.get_all_vendor_point_records_for_johnson.assert_called_with(data_mapping)
        uow_mock.return_value.energy_records.insert_equipment_point_records(insert_list)
        energy_record_compiler.return_value.compile_component_point_records_by_year_span.assert_called_with('1', first_datetime, second_datetime)
        uow_mock.return_value.unmapped_vendor_point_records.delete_all_for_johnson_point.assert_called_with(data_mapping)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.EnergyRecordCompiler")
    def test_add_data_for_mapping_fieldserver(self, energy_record_compiler, uow_mock):
        data_mapping = {'fieldserver_offset': Mock(),
                        'fieldserver_site_id': Mock(),
                        'source': 'fieldserver'}
        first_datetime = datetime(1,1,1)
        second_datetime = datetime(1,1,2)
        unknown_vendor_point_records = [{'value': 1,
                                         'id': Mock(),
                                         'created_on': Mock(),
                                         'weather': Mock(),
                                         'date': first_datetime,
                                         'fieldserver_offset': data_mapping['fieldserver_offset'],
                                         'fieldserver_site_id': data_mapping['fieldserver_site_id'],
                                         'source': 'fieldserver'
                                         },
                                        {'value': 2,
                                         'id': Mock(),
                                         'created_on': Mock(),
                                         'weather': Mock(),
                                         'date': second_datetime,
                                         'fieldserver_offset': data_mapping['fieldserver_offset'],
                                         'fieldserver_site_id': data_mapping['fieldserver_site_id'],
                                         'source': 'fieldserver'
                                         }]
        insert_list = [{'value': 1,
                        'syrx_num': '1',
                        'weather': unknown_vendor_point_records[0]['weather'],
                        'created_on': unknown_vendor_point_records[0]['created_on'],
                        'date': first_datetime},
                       {'value': 2,
                        'syrx_num': '1',
                        'weather': unknown_vendor_point_records[1]['weather'],
                        'created_on': unknown_vendor_point_records[1]['created_on'],
                        'date': second_datetime}]
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        uow_mock.return_value.unmapped_vendor_point_records.get_all_vendor_point_records_for_fieldserver.return_value = unknown_vendor_point_records

        unmapped_syrx_num_handler._add_data_for_mapping(data_mapping, '1')

        uow_mock.return_value.unmapped_vendor_point_records.get_all_vendor_point_records_for_fieldserver.assert_called_with(data_mapping)
        uow_mock.return_value.energy_records.insert_equipment_point_records(insert_list)
        energy_record_compiler.return_value.compile_component_point_records_by_year_span.assert_called_with('1', first_datetime, second_datetime)
        uow_mock.return_value.unmapped_vendor_point_records.delete_all_for_fieldserver_point.assert_called_with(data_mapping)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.EnergyRecordCompiler")
    def test_add_data_for_mapping_invensys(self, energy_record_compiler, uow_mock):
        data_mapping = {'invensys_point_name': Mock(),
                        'invensys_equipment_name': Mock(),
                        'invensys_site_name': Mock(),
                        'source': 'invensys'}
        first_datetime = datetime(1,1,1)
        second_datetime = datetime(1,1,2)
        unknown_vendor_point_records = [{'value': 1,
                                         'id': Mock(),
                                         'created_on': Mock(),
                                         'weather': Mock(),
                                         'date': first_datetime,
                                         'invensys_point_name': data_mapping['invensys_point_name'],
                                         'invensys_equipment_name': data_mapping['invensys_equipment_name'],
                                         'invensys_site_name': Mock(),
                                         'source': 'invensys'
                                         },
                                        {'value': 2,
                                         'id': Mock(),
                                         'created_on': Mock(),
                                         'weather': Mock(),
                                         'date': second_datetime,
                                         'invensys_point_name': data_mapping['invensys_point_name'],
                                         'invensys_equipment_name': data_mapping['invensys_equipment_name'],
                                         'invensys_site_name': Mock(),
                                         'source': 'invensys'
                                         }]
        insert_list = [{'value': 1,
                        'syrx_num': '1',
                        'weather': unknown_vendor_point_records[0]['weather'],
                        'created_on': unknown_vendor_point_records[0]['created_on'],
                        'date': first_datetime},
                       {'value': 2,
                        'syrx_num': '1',
                        'weather': unknown_vendor_point_records[1]['weather'],
                        'created_on': unknown_vendor_point_records[1]['created_on'],
                        'date': second_datetime}]
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        uow_mock.return_value.unmapped_vendor_point_records.get_all_vendor_point_records_for_invensys.return_value = unknown_vendor_point_records

        unmapped_syrx_num_handler._add_data_for_mapping(data_mapping, '1')

        uow_mock.return_value.unmapped_vendor_point_records.get_all_vendor_point_records_for_invensys.assert_called_with(data_mapping)
        uow_mock.return_value.energy_records.insert_equipment_point_records(insert_list)
        energy_record_compiler.return_value.compile_component_point_records_by_year_span.assert_called_with('1', first_datetime, second_datetime)
        uow_mock.return_value.unmapped_vendor_point_records.delete_all_for_invensys_point.assert_called_with(data_mapping)

    @patch("nightly_process.unmapped_syrx_num_handler.UoW")
    @patch("nightly_process.unmapped_syrx_num_handler.EnergyRecordCompiler")
    def test_add_data_for_mapping_siemens(self, energy_record_compiler, uow_mock):
        data_mapping = {'siemens_meter_name': Mock(),
                        'source': 'siemens'}
        first_datetime = datetime(1,1,1)
        second_datetime = datetime(1,1,2)
        unknown_vendor_point_records = [{'value': 1,
                                         'id': Mock(),
                                         'created_on': Mock(),
                                         'weather': Mock(),
                                         'date': first_datetime,
                                         'siemens_meter_name': data_mapping['siemens_meter_name'],
                                         'source': 'siemens'
                                         },
                                        {'value': 2,
                                         'id': Mock(),
                                         'created_on': Mock(),
                                         'weather': Mock(),
                                         'date': second_datetime,
                                         'siemens_meter_name': data_mapping['siemens_meter_name'],
                                         'source': 'siemens'
                                         }]
        insert_list = [{'value': 1,
                        'syrx_num': '1',
                        'weather': unknown_vendor_point_records[0]['weather'],
                        'created_on': unknown_vendor_point_records[0]['created_on'],
                        'date': first_datetime},
                       {'value': 2,
                        'syrx_num': '1',
                        'weather': unknown_vendor_point_records[1]['weather'],
                        'created_on': unknown_vendor_point_records[1]['created_on'],
                        'date': second_datetime}]
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        uow_mock.return_value.unmapped_vendor_point_records.get_all_vendor_point_records_for_siemens.return_value = unknown_vendor_point_records

        unmapped_syrx_num_handler._add_data_for_mapping(data_mapping, '1')

        uow_mock.return_value.unmapped_vendor_point_records.get_all_vendor_point_records_for_siemens.assert_called_with(data_mapping)
        uow_mock.return_value.energy_records.insert_equipment_point_records(insert_list)
        energy_record_compiler.return_value.compile_component_point_records_by_year_span.assert_called_with('1', first_datetime, second_datetime)
        uow_mock.return_value.unmapped_vendor_point_records.delete_all_for_siemens_point.assert_called_with(data_mapping)