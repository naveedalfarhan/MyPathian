from collections import defaultdict
import json
import unittest
import io
import dateutil.parser
import pytz
from mock import patch, Mock, call, MagicMock
from vendor_data_pipeline.johnson_file_handler import JohnsonFileHandler, ProcessJohnsonRecordsSummaryReturn, \
    ProcessJohnsonRecordsReturn
import vendor_data_pipeline.johnson_file_handler


class TestJohnsonFileHandler(unittest.TestCase):
    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler.get_mapped_vendor_points")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler.process_all_johnson_files")
    def test_run(self, process_all_johnson_files_mock, get_mapped_vendor_points_mock, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.run()

        process_all_johnson_files_mock.assert_called_with()
        get_mapped_vendor_points_mock.assert_called_with()

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.listdir")
    @patch("vendor_data_pipeline.johnson_file_handler.os")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler.process_johnson_files_in_dir")
    def test_process_all_johnson_files(self, process_johnson_files_in_dir_mock, os_mock, listdir, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.johnson_grouped_folder = "test_folder_name"
        os_mock.path.join.side_effect = lambda a, b, c: a + "/" + b + "/" + c
        johnson_file_handler.mapped_vendor_points = [{"johnson_site_id": "site_id_1", "johnson_fqr": "fqr_1"},
                                                     {"johnson_site_id": "site_id_1", "johnson_fqr": "fqr_2"}]
        success_dest_dir = johnson_file_handler.get_destination_directory(johnson_file_handler.mapped_vendor_points[0]["johnson_site_id"],
                                                                          johnson_file_handler.mapped_vendor_points[0]["johnson_fqr"])
        os_mock.path.exists.side_effect = lambda (x): True if x == success_dest_dir else False

        listdir.return_value = ["file1", "file2", "file3", "file4", "file5", "file6"]
        johnson_file_handler.process_all_johnson_files()
        process_johnson_files_in_dir_mock.assert_has_calls([call(success_dest_dir)])

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.path.join")
    def test_process_johnson_filename(self, path_join, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_str = Mock()
        johnson_file_handler.process_johnson_file_path = Mock()

        containing_directory = Mock()
        file_name = Mock()

        johnson_file_handler.process_johnson_filename(0, containing_directory, file_name, 1)
        path_join.assert_called_with(containing_directory, file_name)
        johnson_file_handler.process_johnson_file_path.assert_called_with(path_join.return_value)
        assert johnson_file_handler.process_johnson_file_path.call_count == 1

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.path.join")
    def test_process_johnson_filename_exception(self, path_join, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_str = Mock()
        johnson_file_handler.process_johnson_file_path = Mock(side_effect=Exception())

        containing_directory = Mock()
        file_name = Mock()

        johnson_file_handler.process_johnson_filename(0, containing_directory, file_name, 1)
        path_join.assert_called_with(containing_directory, file_name)
        johnson_file_handler.process_johnson_file_path.assert_called_with(path_join.return_value)
        assert johnson_file_handler.logger.exception.call_count == 1

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.NamedTemporaryFile")
    @patch("vendor_data_pipeline.johnson_file_handler.path.join")
    @patch("vendor_data_pipeline.johnson_file_handler.open", create=True)
    @patch("vendor_data_pipeline.johnson_file_handler.remove")
    @patch("vendor_data_pipeline.johnson_file_handler.move")
    def test_process_johnson_file_path_no_bad_records(self, move, remove, open_mock, path_join, named_temporary_file, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_str = Mock()

        summary = ProcessJohnsonRecordsSummaryReturn()
        summary.num_bad_records = 0
        johnson_file_handler.process_johnson_file = Mock(return_value=summary)

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

        johnson_file_handler.process_johnson_file_path(file_path)

        named_temporary_file.assert_called_with(delete=False)
        johnson_file_handler.process_johnson_file.assert_called_with(read_file_mock.__enter__.return_value,
                                                                     good_record_file_mock.__enter__.return_value,
                                                                     bad_record_file_mock)

        remove.assert_has_calls([call(file_path), call(bad_record_file_mock.name)])
        bad_record_file_mock.close.assert_called_with()

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.NamedTemporaryFile")
    @patch("vendor_data_pipeline.johnson_file_handler.path.join")
    @patch("vendor_data_pipeline.johnson_file_handler.open", create=True)
    @patch("vendor_data_pipeline.johnson_file_handler.remove")
    @patch("vendor_data_pipeline.johnson_file_handler.move")
    def test_process_johnson_file_path_with_bad_records(self, move, remove, open_mock, path_join, named_temporary_file, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_str = Mock()

        summary = ProcessJohnsonRecordsSummaryReturn()
        summary.num_bad_records = 1
        johnson_file_handler.process_johnson_file = Mock(return_value=summary)

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

        johnson_file_handler.process_johnson_file_path(file_path)

        named_temporary_file.assert_called_with(delete=False)
        johnson_file_handler.process_johnson_file.assert_called_with(read_file_mock.__enter__.return_value,
                                                                     good_record_file_mock.__enter__.return_value,
                                                                     bad_record_file_mock)

        remove.assert_called_with(file_path)
        bad_record_file_mock.close.assert_called_with()
        move.assert_called_with(bad_record_file_mock.name, file_path)

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_process_johnson_file(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_str = Mock()

        good_record_file_mock = MagicMock()
        bad_record_file_mock = MagicMock()

        summary = ProcessJohnsonRecordsSummaryReturn()
        summary.num_good_records = 3
        summary.num_bad_records = 1
        summary.num_global_vendor_point_records = 2
        johnson_file_handler.process_johnson_records = Mock(return_value=summary)

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

        rv = johnson_file_handler.process_johnson_file(read_file_stream, good_record_file_mock, bad_record_file_mock)

        johnson_file_handler.process_johnson_records.assert_called_with(parsed_list, good_record_file_mock,
                                                                        bad_record_file_mock)
        assert rv.num_good_records == 3 and rv.num_bad_records == 1 and rv.num_global_vendor_point_records == 2

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_process_johnson_file_mass_records(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_str = Mock()

        good_record_file_mock = MagicMock()
        bad_record_file_mock = MagicMock()

        summary = ProcessJohnsonRecordsSummaryReturn()
        summary.num_good_records = 200
        summary.num_bad_records = 0
        summary.num_global_vendor_point_records = 0
        johnson_file_handler.process_johnson_records = Mock(return_value=summary)

        read_file_stream = io.StringIO()
        for i in range(400):
            read_file_stream.write(u'{"name": "record"}\n')

        # add extra record to force small batch for good measure
        read_file_stream.write(u'{"name": "record"}')
        read_file_stream.seek(0)

        parsed_list = [{"name": "record"} for i in range(200)]

        rv = johnson_file_handler.process_johnson_file(read_file_stream, good_record_file_mock, bad_record_file_mock)

        johnson_file_handler.process_johnson_records.assert_has_calls([call(parsed_list, good_record_file_mock,
                                                                            bad_record_file_mock),
                                                                       call(parsed_list, good_record_file_mock,
                                                                            bad_record_file_mock),
                                                                       call([{"name": "record"}], good_record_file_mock,
                                                                            bad_record_file_mock)])
        assert rv.num_good_records == 600

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_process_johnson_records(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_str = Mock()
        johnson_file_handler.handle_unmapped_vendor_points = Mock()

        processed_records = ProcessJohnsonRecordsReturn()
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
        johnson_file_handler.get_processed_johnson_records = Mock(return_value=processed_records)
        johnson_file_handler.make_global_vendor_point_records_unique = Mock(return_value=processed_records.global_vendor_point_records)

        records = [MagicMock(), MagicMock()]
        good_record_file = io.StringIO()
        bad_record_file = io.StringIO()

        rv = johnson_file_handler.process_johnson_records(records, good_record_file, bad_record_file)

        johnson_file_handler.get_processed_johnson_records.assert_called_with(records)

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

        johnson_file_handler.handle_unmapped_vendor_points.assert_called_with(processed_records.unmapped_vendor_points)

        assert rv.num_good_records == 2
        assert rv.num_bad_records == 2
        assert rv.num_unmapped_vendor_points == 2

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._handle_record")
    def test_get_processed_johnson_records_successful(self, _handle_record, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", "test_EP_FQR"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                     "point_type": "EP",
                                                     "global": False}],
                         ("123456", "test_NP_FQR"): [{"syrx_num": "400000-0001-237323-NP-001",
                                                     "point_type": "NP",
                                                     "global": False}],
                         ("123456", "test_PP_FQR"): [{"syrx_num": "400000-0001-237323-PP-001",
                                                     "point_type": "PP",
                                                     "global": False}],
                         ("123456", "test_BP_FQR"): [{"syrx_num": "400000-0001-237323-BP-001",
                                                     "point_type": "BP",
                                                     "global": False}]}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"site_id": "123456", "fqr": "test_EP_FQR", "value": "100.1", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_NP_FQR", "value": "100.2", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_PP_FQR", "value": "100.3", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_BP_FQR", "value": "ON", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_BP_FQR", "value": "OFF", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:15"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                if record["value"].upper() == "ON" or record["value"].upper() == "RUN":
                    record["value"] = 1.0
                elif record["value"].upper() == "OFF" or record["value"].upper() == "STOP":
                    record["value"] = 0.0
            record["timestamp"] = johnson_file_handler.get_string_timestamp(record["timestamp"])
            good_record = {
                "syrx_num": mapping["syrx_num"],
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": johnson_file_handler.date_time_str
            }
            rv.good_records.append(good_record)
        _handle_record.side_effect = handle_record_side_effect

        rv = johnson_file_handler.get_processed_johnson_records(records)

        _handle_record.assert_has_calls([call(mappings_dict[("123456", "test_EP_FQR")][0], records[0],
                                              rv, []),
                                         call(mappings_dict[("123456", "test_NP_FQR")][0], records[1],
                                              rv, []),
                                         call(mappings_dict[("123456", "test_PP_FQR")][0], records[2],
                                              rv, []),
                                         call(mappings_dict[("123456", "test_BP_FQR")][0], records[3],
                                              rv, []),
                                         call(mappings_dict[("123456", "test_BP_FQR")][0], records[4],
                                              rv, [])])

        assert len(rv.good_records) == 5
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.good_records[0] == {"syrx_num": "400000-0001-237323-EP-001",
                                      "timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                      "value": 100.1, "date_added": johnson_file_handler.date_time_str}
        assert rv.good_records[1] == {"syrx_num": "400000-0001-237323-NP-001",
                                      "timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                      "value": 100.2, "date_added": johnson_file_handler.date_time_str}
        assert rv.good_records[2] == {"syrx_num": "400000-0001-237323-PP-001",
                                      "timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                      "value": 100.3, "date_added": johnson_file_handler.date_time_str}
        assert rv.good_records[3] == {"syrx_num": "400000-0001-237323-BP-001",
                                      "timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                      "value": 1.0, "date_added": johnson_file_handler.date_time_str}
        assert rv.good_records[4] == {"syrx_num": "400000-0001-237323-BP-001",
                                      "timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                      "value": 0.0, "date_added": johnson_file_handler.date_time_str}

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._handle_record")
    def test_get_processed_johnson_records_unreliable(self, _handle_record, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", "test_EP_FQR"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                      "point_type": "EP",
                                                      "global": False}]}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"site_id": "123456", "fqr": "test_EP_FQR", "value": 0, "reliability": "Unreliable",
                    "timestamp": "2014-09-07 23:00"}]

        rv = johnson_file_handler.get_processed_johnson_records(records)

        _handle_record.assert_called_with(mappings_dict[("123456", "test_EP_FQR")][0], records[0],
                                          rv, ["Record unreliable"])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "fqr": "test_EP_FQR", "value": 0,
                                     "reliability": "Unreliable", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": johnson_file_handler.date_time_str,
                                               "messages": ["Record unreliable"]}}

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._handle_record")
    def test_get_processed_johnson_records_nonexistent_mapping(self, _handle_record, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"site_id": "123456", "fqr": "test_EP_FQR", "value": 0, "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"}]

        rv = johnson_file_handler.get_processed_johnson_records(records)

        assert not _handle_record.called

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 1
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "fqr": "test_EP_FQR", "value": 0,
                                     "reliability": "Reliable", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": johnson_file_handler.date_time_str,
                                               "messages": ["Could not find vendor mapping"]}}

        assert rv.unmapped_vendor_points[0] == {"source": "johnson", "johnson_site_id": "123456",
                                                "johnson_fqr": "test_EP_FQR",
                                                "date_added": johnson_file_handler.date_time_str}

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._handle_record")
    def test_get_processed_johnson_records_invalid_float_value(self, _handle_record, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", "test_EP_FQR"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                      "point_type": "EP",
                                                      "global": False}]}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"site_id": "123456", "fqr": "test_EP_FQR", "value": "a", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            error_messages.append("Invalid value for energy/numeric/position point")
        _handle_record.side_effect = handle_record_side_effect

        rv = johnson_file_handler.get_processed_johnson_records(records)

        _handle_record.assert_called_with(mappings_dict[("123456", "test_EP_FQR")][0], records[0],
                                          rv, ["Invalid value for energy/numeric/position point"])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "fqr": "test_EP_FQR", "value": "a",
                                     "reliability": "Reliable", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": johnson_file_handler.date_time_str,
                                               "messages": ["Invalid value for energy/numeric/position point"]}}

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._handle_record")
    def test_get_processed_johnson_records_invalid_bool_value(self, _handle_record, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", "test_BP_FQR"): [{"syrx_num": "400000-0001-237323-BP-001",
                                                      "point_type": "BP",
                                                      "global": False}]}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"site_id": "123456", "fqr": "test_BP_FQR", "value": "a", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"}]

        def handle_record_side_effect(mapping, record, rv, error_messages):
            error_messages.append("Invalid value for boolean point")
        _handle_record.side_effect = handle_record_side_effect

        rv = johnson_file_handler.get_processed_johnson_records(records)

        _handle_record.assert_called_with(mappings_dict[("123456", "test_BP_FQR")][0], records[0],
                                          rv, ["Invalid value for boolean point"])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "fqr": "test_BP_FQR", "value": "a",
                                     "reliability": "Reliable", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": johnson_file_handler.date_time_str,
                                               "messages": ["Invalid value for boolean point"]}}

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._handle_global_mapping")
    def test_get_processed_johnson_records_successful_global_single_mapping(self, _handle_global_mapping, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", "test_EP_FQR"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                     "point_type": "EP",
                                                     "global": True}],
                         ("123456", "test_NP_FQR"): [{"syrx_num": "400000-0001-237323-NP-001",
                                                     "point_type": "NP",
                                                     "global": True}],
                         ("123456", "test_PP_FQR"): [{"syrx_num": "400000-0001-237323-PP-001",
                                                     "point_type": "PP",
                                                     "global": True}],
                         ("123456", "test_BP_FQR"): [{"syrx_num": "400000-0001-237323-BP-001",
                                                     "point_type": "BP",
                                                     "global": True}]}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"site_id": "123456", "fqr": "test_EP_FQR", "value": "100.1", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_NP_FQR", "value": "100.2", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_PP_FQR", "value": "100.3", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_BP_FQR", "value": "ON", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_BP_FQR", "value": "OFF", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:15"}]

        def handle_global_mapping_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                if record["value"].upper() == "ON" or record["value"].upper() == "RUN":
                    record["value"] = 1.0
                elif record["value"].upper() == "OFF" or record["value"].upper() == "STOP":
                    record["value"] = 0.0
            record["timestamp"] = johnson_file_handler.get_string_timestamp(record["timestamp"])
            global_record = {
                "source": "johnson",
                "johnson_site_id": record["site_id"],
                "johnson_fqr": record["fqr"],
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": johnson_file_handler.date_time_str
            }
            rv.global_vendor_point_records.append(global_record)
        _handle_global_mapping.side_effect = handle_global_mapping_side_effect

        rv = johnson_file_handler.get_processed_johnson_records(records)

        _handle_global_mapping.assert_has_calls([call(mappings_dict[("123456", "test_EP_FQR")][0], records[0],
                                                      rv, []),
                                                 call(mappings_dict[("123456", "test_NP_FQR")][0], records[1],
                                                      rv, []),
                                                 call(mappings_dict[("123456", "test_PP_FQR")][0], records[2],
                                                      rv, []),
                                                 call(mappings_dict[("123456", "test_BP_FQR")][0], records[3],
                                                      rv, []),
                                                 call(mappings_dict[("123456", "test_BP_FQR")][0], records[4],
                                                      rv, [])])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 5

        assert rv.global_vendor_point_records[0] == {"timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                                     "source": "johnson", "johnson_site_id": "123456",
                                                     "johnson_fqr": "test_EP_FQR",
                                                     "value": 100.1, "date_added": johnson_file_handler.date_time_str}
        assert rv.global_vendor_point_records[1] == {"timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                                     "source": "johnson", "johnson_site_id": "123456",
                                                     "johnson_fqr": "test_NP_FQR",
                                                     "value": 100.2, "date_added": johnson_file_handler.date_time_str}
        assert rv.global_vendor_point_records[2] == {"timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                                     "source": "johnson", "johnson_site_id": "123456",
                                                     "johnson_fqr": "test_PP_FQR",
                                                     "value": 100.3, "date_added": johnson_file_handler.date_time_str}
        assert rv.global_vendor_point_records[3] == {"timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                                     "source": "johnson", "johnson_site_id": "123456",
                                                     "johnson_fqr": "test_BP_FQR",
                                                     "value": 1.0, "date_added": johnson_file_handler.date_time_str}
        assert rv.global_vendor_point_records[4] == {"timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                                     "source": "johnson", "johnson_site_id": "123456",
                                                     "johnson_fqr": "test_BP_FQR",
                                                     "value": 0.0, "date_added": johnson_file_handler.date_time_str}

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._handle_global_mapping")
    def test_get_processed_johnson_records_successful_global_multi_mapping(self, _handle_global_mapping, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", "test_EP_FQR"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                      "point_type": "EP",
                                                      "global": True},
                                                     {"syrx_num": "400000-0002-237323-EP-001",
                                                      "point_type": "EP",
                                                      "global": True}]}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)
        records = [{"site_id": "123456", "fqr": "test_EP_FQR", "value": "100.1", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_EP_FQR", "value": "100.2", "reliability": "Reliable",
                    "timestamp": "2014-09-07 23:15"}]

        def handle_global_mapping_side_effect(mapping, record, rv, error_messages):
            if mapping["point_type"] in ["EP", "NP", "PP"]:
                record["value"] = float(record["value"])
            elif mapping["point_type"] == "BP":
                if record["value"].upper() == "ON" or record["value"].upper() == "RUN":
                    record["value"] = 1.0
                elif record["value"].upper() == "OFF" or record["value"].upper() == "STOP":
                    record["value"] = 0.0
            record["timestamp"] = johnson_file_handler.get_string_timestamp(record["timestamp"])
            global_record = {
                "source": "johnson",
                "johnson_site_id": record["site_id"],
                "johnson_fqr": record["fqr"],
                "timestamp": record["timestamp"],
                "value": record["value"],
                "date_added": johnson_file_handler.date_time_str
            }
            rv.global_vendor_point_records.append(global_record)
        _handle_global_mapping.side_effect = handle_global_mapping_side_effect

        rv = johnson_file_handler.get_processed_johnson_records(records)

        _handle_global_mapping.assert_has_calls([call(mappings_dict[("123456", "test_EP_FQR")][0], records[0],
                                                      rv, []),
                                                 call(mappings_dict[("123456", "test_EP_FQR")][0], records[1],
                                                      rv, [])])

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 0
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 2

        assert rv.global_vendor_point_records[0] == {"timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                                     "source": "johnson", "johnson_site_id": "123456",
                                                     "johnson_fqr": "test_EP_FQR",
                                                     "value": 100.1, "date_added": johnson_file_handler.date_time_str}
        assert rv.global_vendor_point_records[1] == {"timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                                     "source": "johnson", "johnson_site_id": "123456",
                                                     "johnson_fqr": "test_EP_FQR",
                                                     "value": 100.2, "date_added": johnson_file_handler.date_time_str}

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_get_processed_johnson_records_unreliable_global_single_mapping(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", "test_EP_FQR"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                      "point_type": "EP",
                                                      "global": True}],
                         ("123456", "test_EP_FQR_2"): [{"syrx_num": "400000-0002-237323-EP-001",
                                                        "point_type": "EP",
                                                        "global": True}]}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"site_id": "123456", "fqr": "test_EP_FQR", "value": 0, "reliability": "Unreliable",
                    "timestamp": "2014-09-07 23:00"},
                   {"site_id": "123456", "fqr": "test_EP_FQR_2", "value": 0, "reliability": "Unreliable",
                    "timestamp": "2014-09-07 23:00"}]

        rv = johnson_file_handler.get_processed_johnson_records(records)

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 2
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "fqr": "test_EP_FQR", "value": 0,
                                     "reliability": "Unreliable", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": johnson_file_handler.date_time_str,
                                               "messages": ["Record unreliable"]}}
        assert rv.bad_records[1] == {"site_id": "123456", "fqr": "test_EP_FQR_2", "value": 0,
                                     "reliability": "Unreliable", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": johnson_file_handler.date_time_str,
                                               "messages": ["Record unreliable"]}}

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_get_processed_johnson_records_unreliable_global_multi_mapping(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mappings_dict = {("123456", "test_EP_FQR"): [{"syrx_num": "400000-0001-237323-EP-001",
                                                      "point_type": "EP",
                                                      "global": True},
                                                     {"syrx_num": "400000-0002-237323-EP-001",
                                                      "point_type": "EP",
                                                      "global": True}]}
        johnson_file_handler.get_mappings_dict = Mock(return_value=mappings_dict)

        records = [{"site_id": "123456", "fqr": "test_EP_FQR", "value": 0, "reliability": "Unreliable",
                    "timestamp": "2014-09-07 23:00"}]

        rv = johnson_file_handler.get_processed_johnson_records(records)

        assert len(rv.good_records) == 0
        assert len(rv.bad_records) == 1
        assert len(rv.unmapped_vendor_points) == 0
        assert len(rv.global_vendor_point_records) == 0

        assert rv.bad_records[0] == {"site_id": "123456", "fqr": "test_EP_FQR", "value": 0,
                                     "reliability": "Unreliable", "timestamp": "2014-09-07 23:00",
                                     "error": {"date": johnson_file_handler.date_time_str,
                                               "messages": ["Record unreliable"]}}
        
    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_handle_record_successful(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        row = {"site_id": "123456", "fqr": "test_EP_FQR", "value": "100.1", "timestamp": "2014-09-07 23:00"}

        rv = ProcessJohnsonRecordsReturn()
        error_messages = []
        johnson_file_handler._handle_record(mapping, row, rv, error_messages)

        self.assertEqual(len(rv.good_records), 1)
        self.assertEqual(len(rv.bad_records), 0)
        self.assertEqual(len(rv.unmapped_vendor_points), 0)
        self.assertEqual(len(rv.global_vendor_point_records), 0)
        self.assertEqual(len(error_messages), 0)

        self.assertEqual(rv.good_records[0], {"syrx_num": "400000-0001-237323-EP-001",
                                              "timestamp": johnson_file_handler.get_string_timestamp.return_value,
                                              "value": 100.1, "date_added": johnson_file_handler.date_time_str})

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_handle_record_invalid_float_value(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"site_id": "123456", "fqr": "test_EP_FQR", "value": "a", "timestamp": "2014-09-07 23:00"}
        rv = ProcessJohnsonRecordsReturn()
        error_messages = []

        johnson_file_handler._handle_record(mapping, record, rv, error_messages)

        self.assertEqual(len(rv.good_records), 0)
        self.assertEqual(len(error_messages), 1)

        self.assertEqual(error_messages, ["Invalid value for energy/numeric/position point"])

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_handle_record_invalid_bool_value(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}
        record = {"site_id": "123456", "fqr": "test_EP_FQR", "value": "a", "timestamp": "2014-09-07 23:00"}
        rv = ProcessJohnsonRecordsReturn()
        error_messages = []

        johnson_file_handler._handle_record(mapping, record, rv, error_messages)

        self.assertEqual(len(rv.good_records), 0)
        self.assertEqual(len(error_messages), 1)

        self.assertEqual(error_messages, ["Invalid value for boolean point"])

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._get_global_vendor_point_record")
    def test_handle_global_mapping_success(self, _get_global_vendor_point_record, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"site_id": "123456", "fqr": "test_EP_FQR", "value": "100.1", "timestamp": "2014-09-07 23:00"}

        global_record = {
            "source": "johnson", "johnson_site_id": "123456", "johnson_fqr": "test_EP_FQR", "value": 100.1,
            "timestamp": johnson_file_handler.get_string_timestamp.return_value,
            "date_added": johnson_file_handler.date_time_str
        }
        _get_global_vendor_point_record.return_value = global_record

        rv = ProcessJohnsonRecordsReturn()
        error_messages = []

        johnson_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        _get_global_vendor_point_record.assert_called_with(mapping, record, error_messages)

        self.assertEqual(len(error_messages), 0)
        self.assertEqual(len(rv.global_vendor_point_records), 1)

        self.assertEqual(rv.global_vendor_point_records[0], global_record)

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    @patch("vendor_data_pipeline.johnson_file_handler.JohnsonFileHandler._get_global_vendor_point_record")
    def test_handle_global_mapping_fail(self, _get_global_vendor_point_record, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"site_id": "123456", "fqr": "test_EP_FQR", "value": "100.1", "timestamp": "2014-09-07 23:00"}

        global_record = None
        _get_global_vendor_point_record.return_value = global_record

        def get_global_vendor_point_record_side_effect(mapping, record, error_messages):
            error_messages.append("Test")
        _get_global_vendor_point_record.side_effect = get_global_vendor_point_record_side_effect

        rv = ProcessJohnsonRecordsReturn()
        error_messages = []

        johnson_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        _get_global_vendor_point_record.assert_called_with(mapping, record, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(len(rv.global_vendor_point_records), 0)

        self.assertEqual(error_messages[0], "Test")

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_get_global_vendor_point_record_success(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"site_id": "123456", "fqr": "test_EP_FQR", "value": "100.1", "timestamp": "2014-09-07 23:00"}

        global_record = {
            "source": "johnson", "johnson_site_id": "123456", "johnson_fqr": "test_EP_FQR", "value": 100.1,
            "timestamp": johnson_file_handler.get_string_timestamp.return_value,
            "date_added": johnson_file_handler.date_time_str,
            'date': pytz.utc.localize(dateutil.parser.parse(record['timestamp']))
        }

        rv = ProcessJohnsonRecordsReturn()
        error_messages = []

        function_rv = johnson_file_handler._get_global_vendor_point_record(mapping, record, error_messages)

        self.assertEqual(len(error_messages), 0)
        self.assertEqual(function_rv, global_record)

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_get_global_vendor_point_record_invalid_float_value(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-EP-001", "point_type": "EP"}
        record = {"site_id": "123456", "fqr": "test_EP_FQR", "value": "a", "timestamp": "2014-09-07 23:00"}

        rv = ProcessJohnsonRecordsReturn()
        error_messages = []

        function_rv = johnson_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(function_rv, None)

        self.assertEqual(error_messages[0], 'Invalid value for energy/numeric/position point')

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_get_global_vendor_point_record_invalid_bool_value(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.logger = Mock()
        johnson_file_handler.date_time_str = Mock()
        johnson_file_handler.get_string_timestamp = Mock()

        mapping = {"syrx_num": "400000-0001-237323-BP-001", "point_type": "BP"}
        record = {"site_id": "123456", "fqr": "test_EP_FQR", "value": "a", "timestamp": "2014-09-07 23:00"}

        rv = ProcessJohnsonRecordsReturn()
        error_messages = []

        function_rv = johnson_file_handler._handle_global_mapping(mapping, record, rv, error_messages)

        self.assertEqual(len(error_messages), 1)
        self.assertEqual(function_rv, None)

        self.assertEqual(error_messages[0], 'Invalid value for boolean point')

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_get_mappings_dict(self, uow):
        uow.return_value.data_mapping.get_mappings_for_johnson_site_id_fqr.return_value = [
            {"johnson_site_id": "123456", "johnson_fqr": "fqr1", "syrx_num": "syrx_num1"},
            {"johnson_site_id": "123456", "johnson_fqr": "fqr2", "syrx_num": "syrx_num2"},
            {"johnson_site_id": "789012", "johnson_fqr": "fqr3", "syrx_num": "syrx_num3"},
            {"johnson_site_id": "789012", "johnson_fqr": "fqr4", "syrx_num": "syrx_num4"}
        ]
        johnson_file_handler = JohnsonFileHandler()

        records = [{"site_id": "123456", "fqr": "fqr1", "value": 0},
                   {"site_id": "123456", "fqr": "fqr2", "value": 0},
                   {"site_id": "789012", "fqr": "fqr3", "value": 0},
                   {"site_id": "789012", "fqr": "fqr4", "value": 0}]
        keys = [["123456", "fqr1"],
                ["123456", "fqr2"],
                ["789012", "fqr3"],
                ["789012", "fqr4"]]

        ret_val = defaultdict(list)
        ret_val[("123456", "fqr1")].append({"johnson_site_id": "123456", "johnson_fqr": "fqr1", "syrx_num": "syrx_num1"})
        ret_val[("123456", "fqr2")].append({"johnson_site_id": "123456", "johnson_fqr": "fqr2", "syrx_num": "syrx_num2"})
        ret_val[("789012", "fqr3")].append({"johnson_site_id": "789012", "johnson_fqr": "fqr3", "syrx_num": "syrx_num3"})
        ret_val[("789012", "fqr4")].append({"johnson_site_id": "789012", "johnson_fqr": "fqr4", "syrx_num": "syrx_num4"})


        rv = johnson_file_handler.get_mappings_dict(records)

        uow.return_value.data_mapping.get_mappings_for_johnson_site_id_fqr.assert_called_with(keys)

        assert rv == ret_val

    @patch("vendor_data_pipeline.johnson_file_handler.pytz.utc.localize")
    @patch("vendor_data_pipeline.johnson_file_handler.dateutil.parser.parse")
    def test_get_string_timestamp(self, dateutil_parse, pytz_utc_localize):
        timestamp = Mock()

        rv = JohnsonFileHandler.get_string_timestamp(timestamp)

        dateutil_parse.assert_called_with(timestamp)
        pytz_utc_localize.assert_called_with(dateutil_parse.return_value)
        pytz_utc_localize.return_value.strftime.assert_called_with("%Y-%m-%d %H:%M:%S")
        assert rv == pytz_utc_localize.return_value.strftime.return_value

    @patch("vendor_data_pipeline.johnson_file_handler.UoW")
    def test_handle_unmapped_vendor_points(self, uow):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.date_str = "date"

        unmapped_vendor_points = [{"source": "johnson", "johnson_site_id": "123456", "johnson_fqr": "test_EP_FQR"},
                                  {"source": "johnson", "johnson_site_id": "123456", "johnson_fqr": "test_EP_FQR"},
                                  {"source": "johnson", "johnson_site_id": "123456", "johnson_fqr": "test_NP_FQR"}]

        detupled_keys = [["123456", "test_EP_FQR"], ["123456", "test_NP_FQR"]]

        db_query_call = uow.return_value.data_mapping.get_unknown_vendor_points_for_johnson_site_id_fqr
        db_insert_call = uow.return_value.data_mapping.insert_unknown_vendor_points
        db_query_call.return_value = [{"source": "johnson", "johnson_site_id": "123456",
                                       "johnson_fqr": "test_EP_FQR", "date_added": "date"},
                                      {"source": "johnson", "johnson_site_id": "123456",
                                       "johnson_fqr": "test_EP_FQR", "date_added": "date"}]

        johnson_file_handler.handle_unmapped_vendor_points(unmapped_vendor_points)
        db_query_call_args = db_query_call.call_args[0][0]
        assert sorted(db_query_call_args) == sorted(detupled_keys)

        filtered_unmapped_vendor_points = [{"source": "johnson", "johnson_site_id": "123456",
                                            "johnson_fqr": "test_NP_FQR", "date_added": "date"}]

        db_insert_call.assert_called_with(filtered_unmapped_vendor_points)

