from collections import defaultdict
import json
import unittest
import io
import pytz
import dateutil.parser
from mock import patch, Mock, call, MagicMock
from vendor_data_pipeline.fieldserver_file_handler import FieldserverFileHandler, ProcessFieldserverRecordsSummaryReturn, \
    ProcessFieldserverRecordsReturn


class TestFieldserverFileHandler(unittest.TestCase):
    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler.get_mapped_vendor_points")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler.process_all_fieldserver_files")
    def test_run(self, process_all_fieldserver_files_mock, get_mapped_vendor_points_mock, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.run()

        process_all_fieldserver_files_mock.assert_called_with()
        get_mapped_vendor_points_mock.assert_called_with()

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.listdir")
    @patch("vendor_data_pipeline.fieldserver_file_handler.os")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler.process_fieldserver_files_in_dir")
    def test_process_all_fieldserver_files(self, process_fieldserver_files_in_dir_mock, os_mock, listdir, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.fieldserver_grouped_folder = "test_folder_name"
        os_mock.path.join.side_effect = lambda a, b, c: a + "/" + b + "/" + str(c)
        fieldserver_file_handler.mapped_vendor_points = [{"fieldserver_site_id": "site_id_1", "fieldserver_offset": 0},
                                                         {"fieldserver_site_id": "site_id_1", "fieldserver_offset": 1}]

        success_dest_dir = fieldserver_file_handler.get_destination_directory(fieldserver_file_handler.mapped_vendor_points[0]["fieldserver_site_id"],
                                                                              fieldserver_file_handler.mapped_vendor_points[0]["fieldserver_offset"])

        os_mock.path.exists.side_effect = lambda (x): True if x == success_dest_dir else False

        listdir.return_value = ["file1", "file2", "file3", "file4", "file5", "file6"]

        fieldserver_file_handler.process_all_fieldserver_files()
        process_fieldserver_files_in_dir_mock.assert_has_calls([call(success_dest_dir)])

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.path.join")
    def test_process_fieldserver_filename(self, path_join, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_str = Mock()
        fieldserver_file_handler.process_fieldserver_file_path = Mock()

        containing_directory = Mock()
        file_name = Mock()

        fieldserver_file_handler.process_fieldserver_filename(0, containing_directory, file_name, 1)
        path_join.assert_called_with(containing_directory, file_name)
        fieldserver_file_handler.process_fieldserver_file_path.assert_called_with(path_join.return_value)
        assert fieldserver_file_handler.process_fieldserver_file_path.call_count == 1

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.path.join")
    def test_process_fieldserver_filename_exception(self, path_join, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_str = Mock()
        fieldserver_file_handler.process_fieldserver_file_path = Mock(side_effect=Exception())

        containing_directory = Mock()
        file_name = Mock()

        fieldserver_file_handler.process_fieldserver_filename(0, containing_directory, file_name, 1)
        path_join.assert_called_with(containing_directory, file_name)
        fieldserver_file_handler.process_fieldserver_file_path.assert_called_with(path_join.return_value)
        assert fieldserver_file_handler.logger.exception.call_count == 1

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.NamedTemporaryFile")
    @patch("vendor_data_pipeline.fieldserver_file_handler.path.join")
    @patch("vendor_data_pipeline.fieldserver_file_handler.open", create=True)
    @patch("vendor_data_pipeline.fieldserver_file_handler.remove")
    @patch("vendor_data_pipeline.fieldserver_file_handler.move")
    def test_process_fieldserver_file_path_no_bad_records(self, move, remove, open_mock, path_join, named_temporary_file, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_str = Mock()

        summary = ProcessFieldserverRecordsSummaryReturn()
        summary.num_bad_records = 0
        fieldserver_file_handler.process_fieldserver_file = Mock(return_value=summary)

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

        fieldserver_file_handler.process_fieldserver_file_path(file_path)

        named_temporary_file.assert_called_with(delete=False)
        fieldserver_file_handler.process_fieldserver_file.assert_called_with(read_file_mock.__enter__.return_value,
                                                                     good_record_file_mock.__enter__.return_value,
                                                                     bad_record_file_mock)

        remove.assert_has_calls([call(file_path), call(bad_record_file_mock.name)])
        bad_record_file_mock.close.assert_called_with()

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.NamedTemporaryFile")
    @patch("vendor_data_pipeline.fieldserver_file_handler.path.join")
    @patch("vendor_data_pipeline.fieldserver_file_handler.open", create=True)
    @patch("vendor_data_pipeline.fieldserver_file_handler.remove")
    @patch("vendor_data_pipeline.fieldserver_file_handler.move")
    def test_process_fieldserver_file_path_with_bad_records(self, move, remove, open_mock, path_join, named_temporary_file, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_str = Mock()

        summary = ProcessFieldserverRecordsSummaryReturn()
        summary.num_bad_records = 1
        fieldserver_file_handler.process_fieldserver_file = Mock(return_value=summary)

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

        fieldserver_file_handler.process_fieldserver_file_path(file_path)

        named_temporary_file.assert_called_with(delete=False)
        fieldserver_file_handler.process_fieldserver_file.assert_called_with(read_file_mock.__enter__.return_value,
                                                                     good_record_file_mock.__enter__.return_value,
                                                                     bad_record_file_mock)

        remove.assert_called_with(file_path)
        bad_record_file_mock.close.assert_called_with()
        move.assert_called_with(bad_record_file_mock.name, file_path)

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_process_fieldserver_file(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_str = Mock()

        good_record_file_mock = MagicMock()
        bad_record_file_mock = MagicMock()

        summary = ProcessFieldserverRecordsSummaryReturn()
        summary.num_good_records = 3
        summary.num_bad_records = 1
        summary.num_global_vendor_point_records = 2
        fieldserver_file_handler.process_fieldserver_records = Mock(return_value=summary)

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

        rv = fieldserver_file_handler.process_fieldserver_file(read_file_stream, good_record_file_mock, bad_record_file_mock)

        fieldserver_file_handler.process_fieldserver_records.assert_called_with(parsed_list, good_record_file_mock,
                                                                        bad_record_file_mock)
        assert rv.num_good_records == 3 and rv.num_bad_records == 1 and rv.num_global_vendor_point_records == 2

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_process_fieldserver_file_mass_records(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_str = Mock()

        good_record_file_mock = MagicMock()
        bad_record_file_mock = MagicMock()

        summary = ProcessFieldserverRecordsSummaryReturn()
        summary.num_good_records = 200
        summary.num_bad_records = 0
        summary.num_global_vendor_point_records = 0
        fieldserver_file_handler.process_fieldserver_records = Mock(return_value=summary)

        read_file_stream = io.StringIO()
        for i in range(400):
            read_file_stream.write(u'{"name": "record"}\n')

        # add extra record to force small batch for good measure
        read_file_stream.write(u'{"name": "record"}')
        read_file_stream.seek(0)

        parsed_list = [{"name": "record"} for i in range(200)]

        rv = fieldserver_file_handler.process_fieldserver_file(read_file_stream, good_record_file_mock, bad_record_file_mock)

        fieldserver_file_handler.process_fieldserver_records.assert_has_calls([call(parsed_list, good_record_file_mock,
                                                                            bad_record_file_mock),
                                                                       call(parsed_list, good_record_file_mock,
                                                                            bad_record_file_mock),
                                                                       call([{"name": "record"}], good_record_file_mock,
                                                                            bad_record_file_mock)])
        assert rv.num_good_records == 600

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_process_fieldserver_records(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_str = Mock()
        fieldserver_file_handler.handle_unmapped_vendor_points = Mock()

        processed_records = ProcessFieldserverRecordsReturn()
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
            {'name': 'record6'},
            {'name': 'record7'}
        ]
        fieldserver_file_handler.get_processed_fieldserver_records = Mock(return_value=processed_records)
        fieldserver_file_handler.make_global_vendor_point_records_unique = Mock(return_value=processed_records.global_vendor_point_records)

        records = [MagicMock(), MagicMock()]
        good_record_file = io.StringIO()
        bad_record_file = io.StringIO()

        rv = fieldserver_file_handler.process_fieldserver_records(records, good_record_file, bad_record_file)

        fieldserver_file_handler.get_processed_fieldserver_records.assert_called_with(records)

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

        fieldserver_file_handler.handle_unmapped_vendor_points.assert_called_with(processed_records.unmapped_vendor_points)

        assert rv.num_good_records == 2
        assert rv.num_bad_records == 2
        assert rv.num_unmapped_vendor_points == 2

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler._handle_record")
    def test_get_processed_fieldserver_records_successful(self, _handle_record, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", 0): [{"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}],
                         ("123456", 1): [{"syrx_num": "400000-0001-237323-NP-001", "point_type": "NP"}],
                         ("123456", 2): [{"syrx_num": "400000-0001-237323-PP-001", "point_type": "PP"}],
                         ("123456", 3): [{"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}]}
        fieldserver_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"site_id": "123456", "offset": 0, "value": "100.1", "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "offset": 1, "value": "100.2", "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "offset": 2, "value": "100.3", "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "offset": 3, "value": "1.0", "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "offset": 3, "value": "0.0", "timestamp": "2014-09-07 23:15"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                record["value"] = float(record["value"])
                if record["value"] > 0:
                    record["value"] = 1.0
                else:
                    record["value"] = 0.0
            record["timestamp"] = fieldserver_file_handler.get_string_timestamp(record["timestamp"])
            good_record = {
                "syrx_num": mapping["syrx_num"],
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": fieldserver_file_handler.date_time_str
            }
            rv.good_records.append(good_record)
        _handle_record.side_effect = handle_record_side_effect

        rv = fieldserver_file_handler.get_processed_fieldserver_records(records)

        _handle_record.assert_has_calls([call(mappings_dict[("123456", 0)][0], records[0], rv, []),
                                         call(mappings_dict[("123456", 1)][0], records[1], rv, []),
                                         call(mappings_dict[("123456", 2)][0], records[2], rv, []),
                                         call(mappings_dict[("123456", 3)][0], records[3], rv, []),
                                         call(mappings_dict[("123456", 3)][0], records[4], rv, [])])

        assert len(rv.good_records) == 5
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.good_records[0] == {"syrx_num": "400000-0001-237323-EP-001",
                                      "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                      "value": 100.1, "date_added": fieldserver_file_handler.date_time_str}
        assert rv.good_records[1] == {"syrx_num": "400000-0001-237323-NP-001",
                                      "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                      "value": 100.2, "date_added": fieldserver_file_handler.date_time_str}
        assert rv.good_records[2] == {"syrx_num": "400000-0001-237323-PP-001",
                                      "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                      "value": 100.3, "date_added": fieldserver_file_handler.date_time_str}
        assert rv.good_records[3] == {"syrx_num": "400000-0001-237323-BP-001",
                                      "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                      "value": 1.0, "date_added": fieldserver_file_handler.date_time_str}
        assert rv.good_records[4] == {"syrx_num": "400000-0001-237323-BP-001",
                                      "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                      "value": 0.0, "date_added": fieldserver_file_handler.date_time_str}

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler._handle_record")
    def test_get_processed_fieldserver_records_nonexistent_mapping(self, _handle_record, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mappings_dict = {}
        fieldserver_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"site_id": "123456", "offset": 0, "value": "0.0", "timestamp": "2014-09-07 23:00"}]

        rv = fieldserver_file_handler.get_processed_fieldserver_records(records)

        assert not _handle_record.called

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 1
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "offset": 0, "value": "0.0", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": fieldserver_file_handler.date_time_str,
                                               "messages": ["Could not find vendor mapping"]}}

        assert rv.unmapped_vendor_points[0] == {"source": "fieldserver", "fieldserver_site_id": "123456",
                                                "fieldserver_offset": 0,
                                                "date_added": fieldserver_file_handler.date_time_str}

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler._handle_record")
    def test_get_processed_fieldserver_records_invalid_float_value(self, _handle_record, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", 0): [{"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}]}
        fieldserver_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"site_id": "123456", "offset": 0, "value": "a", "timestamp": "2014-09-07 23:00"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            error_messages.append("Invalid value for energy/numeric/position point")
        _handle_record.side_effect = handle_record_side_effect

        rv = fieldserver_file_handler.get_processed_fieldserver_records(records)

        _handle_record.assert_called_with(mappings_dict[("123456", 0)][0], records[0], rv,
                                          ["Invalid value for energy/numeric/position point"])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "offset": 0, "value": "a", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": fieldserver_file_handler.date_time_str,
                                               "messages": ["Invalid value for energy/numeric/position point"]}}

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler._handle_record")
    def test_get_processed_fieldserver_records_invalid_bool_value(self, _handle_record, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", 0): [{"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}]}
        fieldserver_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"site_id": "123456", "offset": 0, "value": "a", "timestamp": "2014-09-07 23:00"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            error_messages.append("Invalid value for boolean point")
        _handle_record.side_effect = handle_record_side_effect

        rv = fieldserver_file_handler.get_processed_fieldserver_records(records)

        _handle_record.assert_called_with(mappings_dict[("123456", 0)][0], records[0], rv,
                                          ["Invalid value for boolean point"])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "offset": 0, "value": "a", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": fieldserver_file_handler.date_time_str,
                                               "messages": ["Invalid value for boolean point"]}}

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler._handle_global_mapping")
    def test_get_processed_fieldserver_records_successful_global_single_mapping(self, _handle_global_mapping, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", 0): [{"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP", "global": True}],
                         ("123456", 1): [{"syrx_num": "400000-0001-237323-NP-001", "point_type": "NP", "global": True}],
                         ("123456", 2): [{"syrx_num": "400000-0001-237323-PP-001", "point_type": "PP", "global": True}],
                         ("123456", 3): [{"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP", "global": True}]}
        fieldserver_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"site_id": "123456", "offset": 0, "value": "100.1", "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "offset": 1, "value": "100.2", "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "offset": 2, "value": "100.3", "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "offset": 3, "value": "1.0", "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "offset": 3, "value": "0.0", "timestamp": "2014-09-07 23:15"}]

        def handle_global_mapping_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                record["value"] = float(record["value"])
                if record["value"] > 0:
                    record["value"] = 1.0
                else:
                    record["value"] = 0.0
            record["timestamp"] = fieldserver_file_handler.get_string_timestamp(record["timestamp"])
            global_record = {
                "source": "fieldserver",
                "fieldserver_site_id": str(record["site_id"]),
                "fieldserver_offset": str(record["offset"]),
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": fieldserver_file_handler.date_time_str
            }
            rv.global_vendor_point_records.append(global_record)
        _handle_global_mapping.side_effect = handle_global_mapping_side_effect

        rv = fieldserver_file_handler.get_processed_fieldserver_records(records)

        _handle_global_mapping.assert_has_calls([call(mappings_dict[("123456", 0)][0], records[0], rv, []),
                                                 call(mappings_dict[("123456", 1)][0], records[1], rv, []),
                                                 call(mappings_dict[("123456", 2)][0], records[2], rv, []),
                                                 call(mappings_dict[("123456", 3)][0], records[3], rv, []),
                                                 call(mappings_dict[("123456", 3)][0], records[4], rv, [])])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 5

        assert rv.global_vendor_point_records[0] == {"source": "fieldserver", "fieldserver_site_id": "123456",
                                                     "fieldserver_offset": "0",
                                                     "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                                     "value": 100.1, "date_added": fieldserver_file_handler.date_time_str}
        assert rv.global_vendor_point_records[1] == {"source": "fieldserver", "fieldserver_site_id": "123456",
                                                     "fieldserver_offset": "1",
                                                     "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                                     "value": 100.2, "date_added": fieldserver_file_handler.date_time_str}
        assert rv.global_vendor_point_records[2] == {"source": "fieldserver", "fieldserver_site_id": "123456",
                                                     "fieldserver_offset": "2",
                                                     "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                                     "value": 100.3, "date_added": fieldserver_file_handler.date_time_str}
        assert rv.global_vendor_point_records[3] == {"source": "fieldserver", "fieldserver_site_id": "123456",
                                                     "fieldserver_offset": "3",
                                                     "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                                     "value": 1.0, "date_added": fieldserver_file_handler.date_time_str}
        assert rv.global_vendor_point_records[4] == {"source": "fieldserver", "fieldserver_site_id": "123456",
                                                     "fieldserver_offset": "3",
                                                     "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                                     "value": 0.0, "date_added": fieldserver_file_handler.date_time_str}

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler._handle_global_mapping")
    def test_get_processed_fieldserver_records_successful_global_multi_mapping(self, _handle_global_mapping, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", 0): [{"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP", "global": True},
                                         {"syrx_num": "400000-0002-237323-NP-001", "point_type": "EP", "global": True}]}
        fieldserver_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"site_id": "123456", "offset": 0, "value": "100.1", "timestamp": "2014-09-07 23:00"}]

        def handle_global_mapping_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                record["value"] = float(record["value"])
                if record["value"] > 0:
                    record["value"] = 1.0
                else:
                    record["value"] = 0.0
            record["timestamp"] = fieldserver_file_handler.get_string_timestamp(record["timestamp"])
            global_record = {
                "source": "fieldserver",
                "fieldserver_site_id": str(record["site_id"]),
                "fieldserver_offset": str(record["offset"]),
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": fieldserver_file_handler.date_time_str
            }
            rv.global_vendor_point_records.append(global_record)
        _handle_global_mapping.side_effect = handle_global_mapping_side_effect

        rv = fieldserver_file_handler.get_processed_fieldserver_records(records)

        _handle_global_mapping.assert_has_calls([call(mappings_dict[("123456", 0)][0], records[0], rv, [])])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 1

        assert rv.global_vendor_point_records[0] == {"source": "fieldserver", "fieldserver_site_id": "123456",
                                                     "fieldserver_offset": "0",
                                                     "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                                     "value": 100.1, "date_added": fieldserver_file_handler.date_time_str}
        
    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_handle_record_successful(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}

        row = {"site_id": "123456", "offset": 0,
               "value": "100.1", "timestamp": "2014-09-07 23:00"}
        rv = ProcessFieldserverRecordsReturn()
        error_messages = []
        fieldserver_file_handler._handle_record(mapping, row, rv, error_messages)

        assert len(rv.good_records) == 1
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0
        assert len(error_messages) == 0

        assert rv.good_records[0] == {"syrx_num": "400000-0001-237323-EP-001",
                                      "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                                      "value": 100.1, "date_added": fieldserver_file_handler.date_time_str}

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_handle_record_invalid_float_value(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"site_id": "123456", "offset": 0,
                  "value": "a", "timestamp": "2014-09-07 23:00"}
        rv = ProcessFieldserverRecordsReturn()
        error_messages = []
        fieldserver_file_handler._handle_record(mapping, record, rv, error_messages)

        assert len(rv.good_records) == 0
        assert len(error_messages) == 1

        assert error_messages == ["Invalid value for energy/numeric/position point"]

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_handle_record_invalid_bool_value(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}
        record = {"site_id": "123456", "offset": 0,
                  "value": "a", "timestamp": "2014-09-07 23:00"}
        rv = ProcessFieldserverRecordsReturn()
        error_messages = []

        fieldserver_file_handler._handle_record(mapping, record, rv, error_messages)

        assert len(error_messages) == 1
        assert len(rv.good_records) == 0
        assert error_messages == ["Invalid value for boolean point"]

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler._get_global_vendor_point_record")
    def test_handle_global_mapping_success(self, _get_global_vendor_point_record, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}
        record = {"site_id": "123456", "offset": 0,
                  "value": "ON", "timestamp": "2014-09-07 23:00"}

        global_record = {"source": "fieldserver", "fieldserver_site_id": "123456", "fieldserver_offset": 0,
                         "value": 1.0,
                         "timestamp": fieldserver_file_handler.get_string_timestamp.return_value,
                         "date_added": fieldserver_file_handler.date_time_str}
        _get_global_vendor_point_record.return_value = global_record

        rv = ProcessFieldserverRecordsReturn()
        error_messages = []
        fieldserver_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        _get_global_vendor_point_record.assert_called_with(mapping, record, error_messages)

        self.assertEqual(len(error_messages), 0)
        self.assertEqual(len(rv.global_vendor_point_records), 1)

        self.assertEqual(rv.global_vendor_point_records[0], global_record)

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    @patch("vendor_data_pipeline.fieldserver_file_handler.FieldserverFileHandler._get_global_vendor_point_record")
    def test_handle_global_mapping_fail(self, _get_global_vendor_point_record, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}
        record = {"site_id": "123456", "offset": 0, "value": "a", "timestamp": "2014-09-07 23:00"}

        def get_global_vendor_point_record_side_effect(mapping, record, error_messages):
            error_messages.append('Test')
        _get_global_vendor_point_record.side_effect = get_global_vendor_point_record_side_effect

        global_record = None
        _get_global_vendor_point_record.return_value = global_record

        rv = ProcessFieldserverRecordsReturn()
        error_messages = []
        fieldserver_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        _get_global_vendor_point_record.assert_called_with(mapping, record, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(len(rv.global_vendor_point_records), 0)

        self.assertEqual(error_messages[0], 'Test')

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_get_global_vendor_point_record_success(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP", "global": True}
        row = {"site_id": "123456", "offset": 0, "value": "100.1", "timestamp": "2014-09-07 23:00"}
        global_record = {
            "source": "fieldserver",
            "fieldserver_site_id": "123456",
            "fieldserver_offset": 0,
            "value": 100.1,
            "timestamp": fieldserver_file_handler.get_string_timestamp(row["timestamp"]),
            "date_added": fieldserver_file_handler.date_time_str,
            'date': pytz.utc.localize(dateutil.parser.parse(row['timestamp']))
        }

        rv = ProcessFieldserverRecordsReturn()
        error_messages = []
        function_rv = fieldserver_file_handler._get_global_vendor_point_record(mapping, row, error_messages)

        self.assertEqual(len(error_messages), 0)
        self.assertEqual(function_rv, global_record)

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_get_global_vendor_point_record_invalid_float_value(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP", "global": True}
        row = {"site_id": "123456", "offset": 0, "value": "a", "timestamp": "2014-09-07 23:00"}
        global_record = None

        rv = ProcessFieldserverRecordsReturn()
        error_messages = []
        function_rv = fieldserver_file_handler._get_global_vendor_point_record(mapping, row, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(error_messages[0], "Invalid value for energy/numeric/position point")
        self.assertEqual(function_rv, global_record)

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_get_global_vendor_point_record_invalid_bool_value(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.logger = Mock()
        fieldserver_file_handler.date_time_str = Mock()
        fieldserver_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "BP", "global": True}
        row = {"site_id": "123456", "offset": 0, "value": "a", "timestamp": "2014-09-07 23:00"}
        global_record = None

        rv = ProcessFieldserverRecordsReturn()
        error_messages = []
        function_rv = fieldserver_file_handler._get_global_vendor_point_record(mapping, row, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(error_messages[0], "Invalid value for boolean point")
        self.assertEqual(function_rv, global_record)

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_get_mappings_dict(self, uow):
        uow.return_value.data_mapping.get_mappings_for_fieldserver_site_id_offset.return_value = [
            {"fieldserver_site_id": "123456", "fieldserver_offset": 0, "syrx_num": "syrx_num1"},
            {"fieldserver_site_id": "123456", "fieldserver_offset": 1, "syrx_num": "syrx_num2"},
            {"fieldserver_site_id": "789012", "fieldserver_offset": 0, "syrx_num": "syrx_num3"},
            {"fieldserver_site_id": "789012", "fieldserver_offset": 1, "syrx_num": "syrx_num4"}
        ]
        fieldserver_file_handler = FieldserverFileHandler()

        records = [{"site_id": "123456", "offset": 0, "value": 0},
                   {"site_id": "123456", "offset": 1, "value": 0},
                   {"site_id": "789012", "offset": 0, "value": 0},
                   {"site_id": "789012", "offset": 1, "value": 0}]
        keys = [["123456", 0],
                ["123456", 1],
                ["789012", 0],
                ["789012", 1]]

        ret_val = defaultdict(list)
        ret_val[("123456", 0)].append({"fieldserver_site_id": "123456",
                                       "fieldserver_offset": 0,
                                       "syrx_num": "syrx_num1"})
        ret_val[("123456", 1)].append({"fieldserver_site_id": "123456",
                                       "fieldserver_offset": 1,
                                       "syrx_num": "syrx_num2"})
        ret_val[("789012", 0)].append({"fieldserver_site_id": "789012",
                                       "fieldserver_offset": 0,
                                       "syrx_num": "syrx_num3"})
        ret_val[("789012", 1)].append({"fieldserver_site_id": "789012",
                                       "fieldserver_offset": 1,
                                       "syrx_num": "syrx_num4"})

        rv = fieldserver_file_handler.get_mappings_dict(records)

        uow.return_value.data_mapping.get_mappings_for_fieldserver_site_id_offset.assert_called_with(keys)

        assert rv == ret_val

    @patch("vendor_data_pipeline.fieldserver_file_handler.pytz.utc.localize")
    @patch("vendor_data_pipeline.fieldserver_file_handler.dateutil.parser.parse")
    def test_get_string_timestamp(self, dateutil_parse, pytz_utc_localize):
        timestamp = Mock()

        rv = FieldserverFileHandler.get_string_timestamp(timestamp)

        dateutil_parse.assert_called_with(timestamp)
        pytz_utc_localize.assert_called_with(dateutil_parse.return_value)
        pytz_utc_localize.return_value.strftime.assert_called_with("%Y-%m-%d %H:%M:%S")
        assert rv == pytz_utc_localize.return_value.strftime.return_value

    @patch("vendor_data_pipeline.fieldserver_file_handler.UoW")
    def test_handle_unmapped_vendor_points(self, uow):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.date_str = "date"

        unmapped_vendor_points = [{"source": "fieldserver", "fieldserver_site_id": "123456", "fieldserver_offset": 0},
                                  {"source": "fieldserver", "fieldserver_site_id": "123456", "fieldserver_offset": 1},
                                  {"source": "fieldserver", "fieldserver_site_id": "123456", "fieldserver_offset": 2}]

        detupled_keys = [["123456", 0], ["123456", 1], ["123456", 2]]

        db_query_call = uow.return_value.data_mapping.get_unknown_vendor_points_for_fieldserver_site_id_offset
        db_query_call.return_value = [{"source": "fieldserver", "fieldserver_site_id": "123456",
                                       "fieldserver_offset": 0, "date_added": "date"},
                                      {"source": "fieldserver", "fieldserver_site_id": "123456",
                                       "fieldserver_offset": 1, "date_added": "date"}]
        db_insert_call = uow.return_value.data_mapping.insert_unknown_vendor_points

        fieldserver_file_handler.handle_unmapped_vendor_points(unmapped_vendor_points)
        db_query_call_args = db_query_call.call_args[0][0]
        assert sorted(db_query_call_args) == sorted(detupled_keys)

        filtered_unmapped_vendor_points = [{"source": "fieldserver", "fieldserver_site_id": "123456",
                                            "fieldserver_offset": 2, "date_added": "date"}]

        db_insert_call.assert_called_with(filtered_unmapped_vendor_points)
