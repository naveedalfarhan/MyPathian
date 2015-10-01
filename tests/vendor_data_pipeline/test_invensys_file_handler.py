from collections import defaultdict
import io
import unittest
import pytz
import dateutil.parser
from flask import json
from mock import Mock, patch, call, MagicMock
from vendor_data_pipeline.invensys_file_handler import InvensysFileHandler, ProcessInvensysRecordsReturn, ProcessInvensysRecordsSummaryReturn

__author__ = 'badams'


class TestInvensysFileHandle(unittest.TestCase):
    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler.get_mapped_vendor_points")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler.process_all_invensys_files")
    def test_run(self, process_all_invensys_files_mock, get_mapped_vendor_points_mock, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.run()

        process_all_invensys_files_mock.assert_called_with()
        get_mapped_vendor_points_mock.assert_called_with()

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.listdir")
    @patch("vendor_data_pipeline.invensys_file_handler.os")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler.process_invensys_files_in_dir")
    def test_process_all_invensys_files(self, process_invensys_files_in_dir_mock, os_mock, listdir, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.invensys_grouped_folder = "test_folder_name"
        os_mock.path.join.side_effect = lambda a, b, c, d: a + "/" + b + "/" + c + "/" + d
        invensys_file_handler.mapped_vendor_points = [{"invensys_site_name": "site_1", "invensys_equipment_name": "eq_1", "invensys_point_name": "p_1"},
                                                      {"invensys_site_name": "site_1", "invensys_equipment_name": "eq_1", "invensys_point_name": "p_2"}]

        success_dest_dir = invensys_file_handler.get_destination_directory(invensys_file_handler.mapped_vendor_points[0]["invensys_site_name"],
                                                                           invensys_file_handler.mapped_vendor_points[0]["invensys_equipment_name"],
                                                                           invensys_file_handler.mapped_vendor_points[0]["invensys_point_name"])

        os_mock.path.exists.side_effect = lambda (x): True if x == success_dest_dir else False

        listdir.return_value = ["file1", "file2", "file3", "file4", "file5", "file6"]

        invensys_file_handler.process_all_invensys_files()
        process_invensys_files_in_dir_mock.assert_has_calls([call(success_dest_dir)])

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.path.join")
    def test_process_invensys_filename(self, path_join, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_str = Mock()
        invensys_file_handler.process_invensys_file_path = Mock()

        containing_directory = Mock()
        file_name = Mock()

        invensys_file_handler.process_invensys_filename(0, containing_directory, file_name, 1)
        path_join.assert_called_with(containing_directory, file_name)
        invensys_file_handler.process_invensys_file_path.assert_called_with(path_join.return_value)
        assert invensys_file_handler.process_invensys_file_path.call_count == 1

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.path.join")
    def test_process_invensys_filename_exception(self, path_join, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_str = Mock()
        invensys_file_handler.process_invensys_file_path = Mock(side_effect=Exception())

        containing_directory = Mock()
        file_name = Mock()

        invensys_file_handler.process_invensys_filename(0, containing_directory, file_name, 1)
        path_join.assert_called_with(containing_directory, file_name)
        invensys_file_handler.process_invensys_file_path.assert_called_with(path_join.return_value)
        assert invensys_file_handler.logger.exception.call_count == 1
        
    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.NamedTemporaryFile")
    @patch("vendor_data_pipeline.invensys_file_handler.path.join")
    @patch("vendor_data_pipeline.invensys_file_handler.open", create=True)
    @patch("vendor_data_pipeline.invensys_file_handler.remove")
    @patch("vendor_data_pipeline.invensys_file_handler.move")
    def test_process_invensys_file_path_no_bad_records(self, move, remove, open_mock, path_join, named_temporary_file, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_str = Mock()

        summary = ProcessInvensysRecordsSummaryReturn()
        summary.num_bad_records = 0
        invensys_file_handler.process_invensys_file = Mock(return_value=summary)

        file_path = MagicMock()

        good_record_file_path = path_join.return_value
        bad_record_file_mock = named_temporary_file.return_value
        good_record_file_mock = MagicMock()
        read_file_mock = MagicMock()

        def open_mock_side_effect(path, mode):
            if path == good_record_file_path and mode == "a":
                return good_record_file_mock
            elif path == file_path and mode == "r":
                return read_file_mock
            else:
                return None
        open_mock.side_effect = open_mock_side_effect

        invensys_file_handler.process_invensys_file_path(file_path)

        named_temporary_file.assert_called_with(delete=False)
        invensys_file_handler.process_invensys_file.assert_called_with(read_file_mock.__enter__.return_value,
                                                                     good_record_file_mock.__enter__.return_value,
                                                                     bad_record_file_mock)

        remove.assert_has_calls([call(file_path), call(bad_record_file_mock.name)])
        bad_record_file_mock.close.assert_called_with()

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.NamedTemporaryFile")
    @patch("vendor_data_pipeline.invensys_file_handler.path.join")
    @patch("vendor_data_pipeline.invensys_file_handler.open", create=True)
    @patch("vendor_data_pipeline.invensys_file_handler.remove")
    @patch("vendor_data_pipeline.invensys_file_handler.move")
    def test_process_invensys_file_path_with_bad_records(self, move, remove, open_mock, path_join, named_temporary_file, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_str = Mock()

        summary = ProcessInvensysRecordsSummaryReturn()
        summary.num_bad_records = 1
        invensys_file_handler.process_invensys_file = Mock(return_value=summary)

        file_path = MagicMock()

        good_record_file_path = path_join.return_value
        bad_record_file_mock = named_temporary_file.return_value
        good_record_file_mock = MagicMock()
        read_file_mock = MagicMock()

        def open_mock_side_effect(path, mode):
            if path == good_record_file_path and mode == "a":
                return good_record_file_mock
            elif path == file_path and mode == "r":
                return read_file_mock
            else:
                return None
        open_mock.side_effect = open_mock_side_effect

        invensys_file_handler.process_invensys_file_path(file_path)

        named_temporary_file.assert_called_with(delete=False)
        invensys_file_handler.process_invensys_file.assert_called_with(read_file_mock.__enter__.return_value,
                                                                     good_record_file_mock.__enter__.return_value,
                                                                     bad_record_file_mock)

        remove.assert_called_with(file_path)
        bad_record_file_mock.close.assert_called_with()
        move.assert_called_with(bad_record_file_mock.name, file_path)

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_process_invensys_file(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_str = Mock()

        good_record_file_mock = MagicMock()
        bad_record_file_mock = MagicMock()

        summary = ProcessInvensysRecordsSummaryReturn()
        summary.num_good_records = 3
        summary.num_bad_records = 1
        summary.num_global_vendor_point_records = 2
        invensys_file_handler.process_invensys_records = Mock(return_value=summary)

        read_file_stream = io.StringIO()
        read_file_stream.write(u'{"name": "record0"}\n'
                               u'{"name": "record1"}\n'
                               u'{"name": "record2"}\n'
                               u'{"name": "record3"}\n'
                               u'{"name": "record4"}\n'
                               u'{"name": "record5"}')
        read_file_stream.seek(0)

        parsed_list = [{"name": "record0"}, {"name": "record1"}, {"name": "record2"}, {"name": "record3"},
                       {"name": "record4"}, {"name": "record5"}]

        rv = invensys_file_handler.process_invensys_file(read_file_stream, good_record_file_mock, bad_record_file_mock)

        invensys_file_handler.process_invensys_records.assert_called_with(parsed_list, good_record_file_mock,
                                                                        bad_record_file_mock)
        assert rv.num_good_records == 3 and rv.num_bad_records == 1 and rv.num_global_vendor_point_records == 2

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_process_invensys_file_mass_records(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_str = Mock()

        good_record_file_mock = MagicMock()
        bad_record_file_mock = MagicMock()

        summary = ProcessInvensysRecordsSummaryReturn()
        summary.num_good_records = 200
        summary.num_bad_records = 0
        summary.num_global_vendor_point_records = 0
        invensys_file_handler.process_invensys_records = Mock(return_value=summary)

        read_file_stream = io.StringIO()
        for i in range(400):
            read_file_stream.write(u'{"name": "record"}\n')

        # add extra record to force small batch for good measure
        read_file_stream.write(u'{"name": "record"}')
        read_file_stream.seek(0)

        parsed_list = [{"name": "record"} for i in range(200)]

        rv = invensys_file_handler.process_invensys_file(read_file_stream, good_record_file_mock, bad_record_file_mock)

        invensys_file_handler.process_invensys_records.assert_has_calls([call(parsed_list, good_record_file_mock,
                                                                            bad_record_file_mock),
                                                                       call(parsed_list, good_record_file_mock,
                                                                            bad_record_file_mock),
                                                                       call([{"name": "record"}], good_record_file_mock,
                                                                            bad_record_file_mock)])
        assert rv.num_good_records == 600

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_process_invensys_records(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_str = Mock()
        invensys_file_handler.handle_unmapped_vendor_points = Mock()

        processed_records = ProcessInvensysRecordsReturn()
        processed_records.good_records = [
            {"name": "record0"},
            {"name": "record1"}
        ]
        processed_records.bad_records = [
            {"name": "record2"},
            {"name": "record3"}
        ]
        processed_records.unmapped_vendor_points = [
            {"name": "record4"},
            {"name": "record5"}
        ]
        processed_records.global_vendor_point_records = [
            {"name": "record6"},
            {"name": "record7"}
        ]
        invensys_file_handler.get_processed_invensys_records = Mock(return_value=processed_records)
        invensys_file_handler.make_global_vendor_point_records_unique = Mock(return_value=processed_records.global_vendor_point_records)

        records = [MagicMock(), MagicMock()]
        good_record_file = io.StringIO()
        bad_record_file = io.StringIO()

        rv = invensys_file_handler.process_invensys_records(records, good_record_file, bad_record_file)

        invensys_file_handler.get_processed_invensys_records.assert_called_with(records)

        good_record_file.seek(0)
        good_records_written_data = good_record_file.read().strip().split("\n")
        assert len(good_records_written_data) == 2
        assert json.loads(good_records_written_data[0]) == {"name": "record0"}
        assert json.loads(good_records_written_data[1]) == {"name": "record1"}

        bad_record_file.seek(0)
        bad_records_written_data = bad_record_file.read().strip().split("\n")
        assert len(bad_records_written_data) == 2
        assert json.loads(bad_records_written_data[0]) == {"name": "record2"}
        assert json.loads(bad_records_written_data[1]) == {"name": "record3"}

        invensys_file_handler.handle_unmapped_vendor_points.assert_called_with(processed_records.unmapped_vendor_points)

        assert rv.num_good_records == 2
        assert rv.num_bad_records == 2
        assert rv.num_unmapped_vendor_points == 2

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler._handle_record")
    def test_get_processed_invensys_records_successful(self, _handle_record, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("Test Site", "Test Equip", "test_Equip_EP"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                                         "point_type": "EP"}],
                         ("Test Site", "Test Equip", "test_Equip_NP"): [{"syrx_num": "400000-0001-237323-NP-001",
                                                                         "point_type": "NP"}],
                         ("Test Site", "Test Equip", "test_Equip_PP"): [{"syrx_num": "400000-0001-237323-PP-001",
                                                                         "point_type": "PP"}],
                         ("Test Site", "Test Equip", "test_Equip_BP"): [{"syrx_num": "400000-0001-237323-BP-001",
                                                                         "point_type": "BP"}]}
        invensys_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_EP", "value": "100.1"},
                   {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_NP", "value": "100.2"},
                   {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_PP", "value": "100.3"},
                   {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_BP", "value": "ON"},
                   {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_BP", "value": "OFF"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                if record["value"].upper() == "ON" or record["value"].upper() == "RUN":
                    record["value"] = 1.0
                elif record["value"].upper() == "OFF" or record["value"].upper() == "STOP":
                    record["value"] = 0.0
            record["timestamp"] = invensys_file_handler.get_string_timestamp(record["timestamp"])
            good_record = {
                "syrx_num": mapping["syrx_num"],
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": invensys_file_handler.date_time_str
            }
            rv.good_records.append(good_record)
        _handle_record.side_effect = handle_record_side_effect

        rv = invensys_file_handler.get_processed_invensys_records(records)

        _handle_record.assert_has_calls([call(mappings_dict[("Test Site", "Test Equip", "test_Equip_EP")][0],
                                              records[0], rv, []),
                                         call(mappings_dict[("Test Site", "Test Equip", "test_Equip_NP")][0],
                                              records[1], rv, []),
                                         call(mappings_dict[("Test Site", "Test Equip", "test_Equip_PP")][0],
                                              records[2], rv, []),
                                         call(mappings_dict[("Test Site", "Test Equip", "test_Equip_BP")][0],
                                              records[3], rv, []),
                                         call(mappings_dict[("Test Site", "Test Equip", "test_Equip_BP")][0],
                                              records[4], rv, [])])

        assert len(rv.good_records) == 5
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.good_records[0] == {"syrx_num": "400000-0001-237323-EP-001",
                                      "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                      "value": 100.1, "date_added": invensys_file_handler.date_time_str}
        assert rv.good_records[1] == {"syrx_num": "400000-0001-237323-NP-001",
                                      "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                      "value": 100.2, "date_added": invensys_file_handler.date_time_str}
        assert rv.good_records[2] == {"syrx_num": "400000-0001-237323-PP-001",
                                      "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                      "value": 100.3, "date_added": invensys_file_handler.date_time_str}
        assert rv.good_records[3] == {"syrx_num": "400000-0001-237323-BP-001",
                                      "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                      "value": 1.0, "date_added": invensys_file_handler.date_time_str}
        assert rv.good_records[4] == {"syrx_num": "400000-0001-237323-BP-001",
                                      "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                      "value": 0.0, "date_added": invensys_file_handler.date_time_str}

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler._handle_record")
    def test_get_processed_invensys_records_nonexistent_mapping(self, _handle_record, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mappings_dict = {}
        invensys_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_EP", "value": "100.1"}]

        rv = invensys_file_handler.get_processed_invensys_records(records)

        assert not _handle_record.called

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 1
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"invensys_site_name": "Test Site",
                                     "invensys_equipment_name": "Test Equip",
                                     "invensys_point_name": "test_Equip_EP", "value": "100.1",
                                     "timestamp": "2014-07-10T11:00:00.241-04:00",
                                     "error": {"date": invensys_file_handler.date_time_str,
                                               "messages": ["Could not find vendor mapping"]}}

        assert rv.unmapped_vendor_points[0] == {"source": "invensys", "invensys_site_name": "Test Site",
                                                "invensys_equipment_name": "Test Equip",
                                                "invensys_point_name": "test_Equip_EP",
                                                "date_added": invensys_file_handler.date_time_str}
    
    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler._handle_record")
    def test_get_processed_invensys_records_invalid_float_value(self, _handle_record, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("Test Site", "Test Equip", "test_Equip_EP"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                                         "point_type": "EP"}]}
        invensys_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_EP", "value": "a"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            error_messages.append("Invalid value for energy/numeric/position point")
        _handle_record.side_effect = handle_record_side_effect

        rv = invensys_file_handler.get_processed_invensys_records(records)

        _handle_record.assert_called_with(mappings_dict[("Test Site", "Test Equip", "test_Equip_EP")][0], records[0],
                                          rv, ["Invalid value for energy/numeric/position point"])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"invensys_site_name": "Test Site",
                                     "invensys_equipment_name": "Test Equip",
                                     "invensys_point_name": "test_Equip_EP", "value": "a",
                                     "timestamp": "2014-07-10T11:00:00.241-04:00",
                                     "error": {"date": invensys_file_handler.date_time_str,
                                               "messages": ["Invalid value for energy/numeric/position point"]}}
    
    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler._handle_record")
    def test_get_processed_invensys_records_invalid_bool_value(self, _handle_record, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("Test Site", "Test Equip", "test_Equip_BP"): [{"syrx_num": "400000-0001-237323-BP-001",
                                                                         "point_type": "BP"}]}
        invensys_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_BP", "value": "a"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            error_messages.append("Invalid value for boolean point")
        _handle_record.side_effect = handle_record_side_effect

        rv = invensys_file_handler.get_processed_invensys_records(records)

        _handle_record.assert_called_with(mappings_dict[("Test Site", "Test Equip", "test_Equip_BP")][0], records[0],
                                          rv, ["Invalid value for boolean point"])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"invensys_site_name": "Test Site",
                                     "invensys_equipment_name": "Test Equip",
                                     "invensys_point_name": "test_Equip_BP",
                                     "timestamp": "2014-07-10T11:00:00.241-04:00",
                                     "value": "a",
                                     "error": {"date": invensys_file_handler.date_time_str,
                                               "messages": ["Invalid value for boolean point"]}}

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler._handle_global_mapping")
    def test_get_processed_invensys_records_successful_global_single_mapping(self, _handle_global_mapping, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("Test Site", "Test Equip", "test_Equip_EP"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                                         "point_type": "EP",
                                                                         "global": True}],
                         ("Test Site", "Test Equip", "test_Equip_NP"): [{"syrx_num": "400000-0001-237323-NP-001",
                                                                         "point_type": "NP",
                                                                         "global": True}],
                         ("Test Site", "Test Equip", "test_Equip_PP"): [{"syrx_num": "400000-0001-237323-PP-001",
                                                                         "point_type": "PP",
                                                                         "global": True}],
                         ("Test Site", "Test Equip", "test_Equip_BP"): [{"syrx_num": "400000-0001-237323-BP-001",
                                                                         "point_type": "BP",
                                                                         "global": True}]}
        invensys_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_EP", "value": "100.1"},
                   {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_NP", "value": "100.2"},
                   {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_PP", "value": "100.3"},
                   {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_BP", "value": "ON"},
                   {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_BP", "value": "OFF"}]

        def handle_global_mapping_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                if record["value"].upper() == "ON" or record["value"].upper() == "RUN":
                    record["value"] = 1.0
                elif record["value"].upper() == "OFF" or record["value"].upper() == "STOP":
                    record["value"] = 0.0
            record["timestamp"] = invensys_file_handler.get_string_timestamp(record["timestamp"])
            global_record = {
                "source": "invensys",
                "invensys_site_name": record["invensys_site_name"],
                "invensys_equipment_name": record["invensys_equipment_name"],
                "invensys_point_name": record["invensys_point_name"],
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": invensys_file_handler.date_time_str
            }
            rv.global_vendor_point_records.append(global_record)
        _handle_global_mapping.side_effect = handle_global_mapping_side_effect

        rv = invensys_file_handler.get_processed_invensys_records(records)

        _handle_global_mapping.assert_has_calls([call(mappings_dict[("Test Site", "Test Equip", "test_Equip_EP")][0],
                                                      records[0], rv, []),
                                                 call(mappings_dict[("Test Site", "Test Equip", "test_Equip_NP")][0],
                                                      records[1], rv, []),
                                                 call(mappings_dict[("Test Site", "Test Equip", "test_Equip_PP")][0],
                                                      records[2], rv, []),
                                                 call(mappings_dict[("Test Site", "Test Equip", "test_Equip_BP")][0],
                                                      records[3], rv, []),
                                                 call(mappings_dict[("Test Site", "Test Equip", "test_Equip_BP")][0],
                                                      records[4], rv, [])])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 5

        assert rv.global_vendor_point_records[0] == {"source": "invensys", "invensys_site_name": "Test Site",
                                                     "invensys_equipment_name": "Test Equip",
                                                     "invensys_point_name": "test_Equip_EP",
                                                     "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                                     "value": 100.1, "date_added": invensys_file_handler.date_time_str}
        assert rv.global_vendor_point_records[1] == {"source": "invensys", "invensys_site_name": "Test Site",
                                                     "invensys_equipment_name": "Test Equip",
                                                     "invensys_point_name": "test_Equip_NP",
                                                     "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                                     "value": 100.2, "date_added": invensys_file_handler.date_time_str}
        assert rv.global_vendor_point_records[2] == {"source": "invensys", "invensys_site_name": "Test Site",
                                                     "invensys_equipment_name": "Test Equip",
                                                     "invensys_point_name": "test_Equip_PP",
                                                     "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                                     "value": 100.3, "date_added": invensys_file_handler.date_time_str}
        assert rv.global_vendor_point_records[3] == {"source": "invensys", "invensys_site_name": "Test Site",
                                                     "invensys_equipment_name": "Test Equip",
                                                     "invensys_point_name": "test_Equip_BP",
                                                     "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                                     "value": 1.0, "date_added": invensys_file_handler.date_time_str}
        assert rv.global_vendor_point_records[4] == {"source": "invensys", "invensys_site_name": "Test Site",
                                                     "invensys_equipment_name": "Test Equip",
                                                     "invensys_point_name": "test_Equip_BP",
                                                     "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                                     "value": 0.0, "date_added": invensys_file_handler.date_time_str}

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler._handle_global_mapping")
    def test_get_processed_invensys_records_successful_global_multi_mapping(self, _handle_global_mapping, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("Test Site", "Test Equip", "test_Equip_EP"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                                         "point_type": "EP",
                                                                         "global": True},
                                                                        {"syrx_num": "400000-0002-237323-EP-001",
                                                                         "point_type": "EP",
                                                                         "global": True}]}
        invensys_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Test Site",
                    "invensys_equipment_name": "Test Equip", "invensys_point_name": "test_Equip_EP", "value": "100.1"}]

        def handle_global_mapping_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                if record["value"].upper() == "ON" or record["value"].upper() == "RUN":
                    record["value"] = 1.0
                elif record["value"].upper() == "OFF" or record["value"].upper() == "STOP":
                    record["value"] = 0.0
            record["timestamp"] = invensys_file_handler.get_string_timestamp(record["timestamp"])
            global_record = {
                "source": "invensys",
                "invensys_site_name": record["invensys_site_name"],
                "invensys_equipment_name": record["invensys_equipment_name"],
                "invensys_point_name": record["invensys_point_name"],
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": invensys_file_handler.date_time_str
            }
            rv.global_vendor_point_records.append(global_record)
        _handle_global_mapping.side_effect = handle_global_mapping_side_effect

        rv = invensys_file_handler.get_processed_invensys_records(records)

        _handle_global_mapping.assert_has_calls([call(mappings_dict[("Test Site", "Test Equip", "test_Equip_EP")][0],
                                                      records[0], rv, [])])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 1

        assert rv.global_vendor_point_records[0] == {"source": "invensys", "invensys_site_name": "Test Site",
                                                     "invensys_equipment_name": "Test Equip",
                                                     "invensys_point_name": "test_Equip_EP",
                                                     "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                                     "value": 100.1, "date_added": invensys_file_handler.date_time_str}

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_handle_record_successful(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        row = {"invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
               "invensys_point_name": "point_1", "value": "100.1", "timestamp": "2014-09-07 23:00"}

        rv = ProcessInvensysRecordsReturn()
        error_messages = []
        invensys_file_handler._handle_record(mapping, row, rv, error_messages)

        self.assertEqual(len(rv.good_records), 1)
        self.assertEqual(len(rv.bad_records), 0)
        self.assertEqual(len(rv.unmapped_vendor_points), 0)
        self.assertEqual(len(rv.global_vendor_point_records), 0)
        self.assertEqual(len(error_messages), 0)

        self.assertEqual(rv.good_records[0], {"syrx_num": "400000-0001-237323-EP-001",
                                              "timestamp": invensys_file_handler.get_string_timestamp.return_value,
                                              "value": 100.1, "date_added": invensys_file_handler.date_time_str})

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_handle_record_invalid_float_value(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
                  "invensys_point_name": "point_1", "value": "a", "timestamp": "2014-09-07 23:00"}
        rv = ProcessInvensysRecordsReturn()
        error_messages = []

        invensys_file_handler._handle_record(mapping, record, rv, error_messages)

        self.assertEqual(len(rv.good_records), 0)
        self.assertEqual(len(error_messages), 1)

        self.assertEqual(error_messages, ["Invalid value for energy/numeric/position point"])

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_handle_record_invalid_bool_value(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}
        record = {"invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
                  "invensys_point_name": "point_1", "value": "a", "timestamp": "2014-09-07 23:00"}
        rv = ProcessInvensysRecordsReturn()
        error_messages = []

        invensys_file_handler._handle_record(mapping, record, rv, error_messages)

        self.assertEqual(len(rv.good_records), 0)
        self.assertEqual(len(error_messages), 1)

        self.assertEqual(error_messages, ["Invalid value for boolean point"])

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler._get_global_vendor_point_record")
    def test_handle_global_mapping_success(self, _get_global_vendor_point_record, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
                  "invensys_point_name": "point_1", "value": "100.1", "timestamp": "2014-09-07 23:00"}

        global_record = {
            "source": "invensys", "invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
            "invensys_point_name": "point_1", "value": 100.1,
            "timestamp": invensys_file_handler.get_string_timestamp.return_value,
            "date_added": invensys_file_handler.date_time_str
        }
        _get_global_vendor_point_record.return_value = global_record

        rv = ProcessInvensysRecordsReturn()
        error_messages = []

        invensys_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        _get_global_vendor_point_record.assert_called_with(mapping, record, error_messages)

        self.assertEqual(len(error_messages), 0)
        self.assertEqual(len(rv.global_vendor_point_records), 1)

        self.assertEqual(rv.global_vendor_point_records[0], global_record)

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    @patch("vendor_data_pipeline.invensys_file_handler.InvensysFileHandler._get_global_vendor_point_record")
    def test_handle_global_mapping_fail(self, _get_global_vendor_point_record, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
                  "invensys_point_name": "point_1", "value": "100.1", "timestamp": "2014-09-07 23:00"}

        global_record = None
        _get_global_vendor_point_record.return_value = global_record

        def get_global_vendor_point_record_side_effect(mapping, record, error_messages):
            error_messages.append("Test")
        _get_global_vendor_point_record.side_effect = get_global_vendor_point_record_side_effect

        rv = ProcessInvensysRecordsReturn()
        error_messages = []

        invensys_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        _get_global_vendor_point_record.assert_called_with(mapping, record, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(len(rv.global_vendor_point_records), 0)

        self.assertEqual(error_messages[0], "Test")

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_get_global_vendor_point_record_success(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
                  "invensys_point_name": "point_1", "value": "100.1", "timestamp": "2014-09-07 23:00"}

        global_record = {
            "source": "invensys", "invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
            "invensys_point_name": "point_1", "value": 100.1,
            "timestamp": invensys_file_handler.get_string_timestamp.return_value,
            "date_added": invensys_file_handler.date_time_str,
            "date": pytz.utc.localize(dateutil.parser.parse(record['timestamp']))
        }

        rv = ProcessInvensysRecordsReturn()
        error_messages = []

        function_rv = invensys_file_handler._get_global_vendor_point_record(mapping, record, error_messages)

        self.assertEqual(len(error_messages), 0)
        self.assertEqual(function_rv, global_record)

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_get_global_vendor_point_record_invalid_float_value(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
                  "invensys_point_name": "point_1", "value": "a", "timestamp": "2014-09-07 23:00"}

        rv = ProcessInvensysRecordsReturn()
        error_messages = []

        function_rv = invensys_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(function_rv, None)

        self.assertEqual(error_messages[0], 'Invalid value for energy/numeric/position point')

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_get_global_vendor_point_record_invalid_bool_value(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.logger = Mock()
        invensys_file_handler.date_time_str = Mock()
        invensys_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}
        record = {"invensys_site_name": "site_1", "invensys_equipment_name": "equip_1",
                  "invensys_point_name": "point_1", "value": "a", "timestamp": "2014-09-07 23:00"}

        rv = ProcessInvensysRecordsReturn()
        error_messages = []

        function_rv = invensys_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(function_rv, None)

        self.assertEqual(error_messages[0], 'Invalid value for boolean point')
        
    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_get_mappings_dict(self, uow):
        uow.return_value.data_mapping.get_mappings_for_invensys_site_equipment_point.return_value = [
            {"invensys_site_name": "123456", "invensys_equipment_name": "e123456", "invensys_point_name": "p123456", "syrx_num": "syrx_num1"},
            {"invensys_site_name": "654321", "invensys_equipment_name": "e654321", "invensys_point_name": "p654321", "syrx_num": "syrx_num2"},
            {"invensys_site_name": "321456", "invensys_equipment_name": "e321456", "invensys_point_name": "p321456", "syrx_num": "syrx_num3"},
            {"invensys_site_name": "321456", "invensys_equipment_name": "e321456", "invensys_point_name": "p321654", "syrx_num": "syrx_num4"}
        ]
        invensys_file_handler = InvensysFileHandler()

        records = [{"invensys_site_name": "123456", "invensys_equipment_name": "e123456", "invensys_point_name": "p123456", "value": "0"},
                   {"invensys_site_name": "654321", "invensys_equipment_name": "e654321", "invensys_point_name": "p654321", "value": "0"},
                   {"invensys_site_name": "321456", "invensys_equipment_name": "e321456", "invensys_point_name": "p321456", "value": "0"},
                   {"invensys_site_name": "321456", "invensys_equipment_name": "e321456", "invensys_point_name": "p321654", "value": "0"},]
        keys = [["123456", "e123456", "p123456"],
                ["654321", "e654321", "p654321"],
                ["321456", "e321456", "p321456"],
                ["321456", "e321456", "p321654"]]

        ret_val = defaultdict(list)
        ret_val[("123456", "e123456", "p123456")].append({"invensys_site_name": "123456",
                                                          "invensys_equipment_name": "e123456",
                                                          "invensys_point_name": "p123456", "syrx_num": "syrx_num1"})
        ret_val[("654321", "e654321", "p654321")].append({"invensys_site_name": "654321",
                                                          "invensys_equipment_name": "e654321",
                                                          "invensys_point_name": "p654321", "syrx_num": "syrx_num2"})
        ret_val[("321456", "e321456", "p321456")].append({"invensys_site_name": "321456",
                                                          "invensys_equipment_name": "e321456",
                                                          "invensys_point_name": "p321456", "syrx_num": "syrx_num3"})
        ret_val[("321456", "e321456", "p321654")].append({"invensys_site_name": "321456",
                                                          "invensys_equipment_name": "e321456",
                                                          "invensys_point_name": "p321654", "syrx_num": "syrx_num4"})

        rv = invensys_file_handler.get_mappings_dict(records)

        uow.return_value.data_mapping.get_mappings_for_invensys_site_equipment_point.assert_called_with(keys)

        assert rv == ret_val
        
    @patch("vendor_data_pipeline.invensys_file_handler.pytz.utc.localize")
    @patch("vendor_data_pipeline.invensys_file_handler.dateutil.parser.parse")
    def test_get_string_timestamp(self, dateutil_parse, pytz_utc_localize):
        timestamp = Mock()

        rv = InvensysFileHandler.get_string_timestamp(timestamp)

        dateutil_parse.assert_called_with(timestamp)
        pytz_utc_localize.assert_called_with(dateutil_parse.return_value)
        pytz_utc_localize.return_value.strftime.assert_called_with("%Y-%m-%d %H:%M:%S")
        assert rv == pytz_utc_localize.return_value.strftime.return_value

    @patch("vendor_data_pipeline.invensys_file_handler.UoW")
    def test_handle_unmapped_vendor_points(self, uow):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.date_str = "date"

        unmapped_vendor_points = [{"source": "invensys", "invensys_site_name": "123456",
                                   "invensys_equipment_name": "test_Equip",
                                   "invensys_point_name": "test_equip_EP"},
                                  {"source": "invensys", "invensys_site_name": "123456",
                                   "invensys_equipment_name": "test_Equip",
                                   "invensys_point_name": "test_equip_EP"},
                                  {"source": "invensys", "invensys_site_name": "123456",
                                   "invensys_equipment_name": "test_Equip",
                                   "invensys_point_name": "test_equip_NP"}]

        detupled_keys = [["123456", "test_Equip", "test_equip_EP"], ["123456", "test_Equip", "test_equip_NP"]]

        db_query_call = uow.return_value.data_mapping.get_unknown_vendor_points_for_invensys_site_equipment_point
        db_insert_call = uow.return_value.data_mapping.insert_unknown_vendor_points
        db_query_call.return_value = [{"source": "invensys", "invensys_site_name": "123456",
                                       "invensys_equipment_name": "test_Equip",
                                       "invensys_point_name": "test_equip_EP", "date_added": "date"},
                                      {"source": "invensys", "invensys_site_name": "123456",
                                       "invensys_equipment_name": "test_Equip",
                                       "invensys_point_name": "test_equip_EP", "date_added": "date"}]

        invensys_file_handler.handle_unmapped_vendor_points(unmapped_vendor_points)
        db_query_call_args = db_query_call.call_args[0][0]
        assert sorted(db_query_call_args) == sorted(detupled_keys)

        filtered_unmapped_vendor_points = [{"source": "invensys", "invensys_site_name": "123456",
                                            "invensys_equipment_name": "test_Equip",
                                            "invensys_point_name": "test_equip_NP", "date_added": "date"}]

        db_insert_call.assert_called_with(filtered_unmapped_vendor_points)
