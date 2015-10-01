import json
import unittest
import io
import datetime
from mock import Mock, patch, call, MagicMock
import pytz
from vendor_data_pipeline.syrx_file_handler import SyrxFileHandler, ProcessSyrxRecordsReturn, \
    EquipmentPointRecordsReturn, RecordRange


class TestSyrxFileHandler(unittest.TestCase):
    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.listdir")
    def test_process_all_syrx_files(self, listdir, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.logger = Mock()
        syrx_file_handler.syrx_upload_folder = Mock()
        syrx_file_handler.process_syrx_filename = Mock()
        syrx_file_handler.process_syrx_filename.return_value = []
        syrx_file_handler.compile_equipment_point_records = Mock()
        listdir.return_value = ["file1", "file2", "file3", "file4", "file5", "file6"]

        syrx_file_handler.process_all_syrx_files()
        syrx_file_handler.process_syrx_filename.assert_has_calls([call(0, "file1", 6),
                                                                  call(1, "file2", 6),
                                                                  call(2, "file3", 6),
                                                                  call(3, "file4", 6),
                                                                  call(4, "file5", 6),
                                                                  call(5, "file6", 6)])

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.path.join")
    def test_process_syrx_filename(self, path_join, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.logger = Mock()
        syrx_file_handler.syrx_upload_folder = Mock()
        syrx_file_handler.process_syrx_file_path = Mock()

        file_name = Mock()

        syrx_file_handler.process_syrx_filename(0, file_name, 1)
        path_join.assert_called_with(syrx_file_handler.syrx_upload_folder, file_name)
        syrx_file_handler.process_syrx_file_path.assert_called_with(path_join.return_value)
        assert syrx_file_handler.process_syrx_file_path.call_count == 1

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.path.join")
    def test_process_johnson_filename_exception(self, path_join, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.logger = Mock()
        syrx_file_handler.syrx_upload_folder = Mock()
        syrx_file_handler.date_str = Mock()
        syrx_file_handler.process_syrx_file_path = Mock(side_effect=Exception())

        file_name = Mock()

        syrx_file_handler.process_syrx_filename(0, file_name, 1)
        path_join.assert_called_with(syrx_file_handler.syrx_upload_folder, file_name)
        syrx_file_handler.process_syrx_file_path.assert_called_with(path_join.return_value)
        assert syrx_file_handler.logger.exception.call_count == 1

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.NamedTemporaryFile")
    @patch("vendor_data_pipeline.syrx_file_handler.path.join")
    @patch("vendor_data_pipeline.syrx_file_handler.open", create=True)
    @patch("vendor_data_pipeline.syrx_file_handler.remove")
    @patch("vendor_data_pipeline.syrx_file_handler.move")
    def test_process_syrx_file_path_no_bad_records(self, move, remove, open_mock, path_join, named_temporary_file, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.logger = Mock()
        syrx_file_handler.syrx_upload_folder = Mock()
        syrx_file_handler.date_str = Mock()

        summary = ProcessSyrxRecordsReturn()
        summary.num_bad_records = 0
        syrx_file_handler.process_syrx_file = Mock(return_value=summary)

        file_path = MagicMock()

        bad_record_file_mock = named_temporary_file.return_value
        read_file_mock = MagicMock()

        def open_mock_side_effect(path, mode):
            if path == file_path and mode == "r":
                return read_file_mock
            else:
                return None
        open_mock.side_effect = open_mock_side_effect

        syrx_file_handler.process_syrx_file_path(file_path)

        named_temporary_file.assert_called_with(delete=False)
        syrx_file_handler.process_syrx_file.assert_called_with(read_file_mock.__enter__.return_value,
                                                               bad_record_file_mock)

        remove.assert_has_calls([call(file_path), call(bad_record_file_mock.name)])
        bad_record_file_mock.close.assert_called_with()

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.NamedTemporaryFile")
    @patch("vendor_data_pipeline.syrx_file_handler.path.join")
    @patch("vendor_data_pipeline.syrx_file_handler.open", create=True)
    @patch("vendor_data_pipeline.syrx_file_handler.remove")
    @patch("vendor_data_pipeline.syrx_file_handler.move")
    def test_process_syrx_file_path_with_bad_records(self, move, remove, open_mock, path_join, named_temporary_file, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.logger = Mock()
        syrx_file_handler.syrx_upload_folder = Mock()
        syrx_file_handler.date_str = Mock()

        summary = ProcessSyrxRecordsReturn()
        summary.num_bad_records = 1
        syrx_file_handler.process_syrx_file = Mock(return_value=summary)

        file_path = MagicMock()

        bad_record_file_mock = named_temporary_file.return_value
        read_file_mock = MagicMock()

        def open_mock_side_effect(path, mode):
            if path == file_path and mode == "r":
                return read_file_mock
            else:
                return None
        open_mock.side_effect = open_mock_side_effect

        syrx_file_handler.process_syrx_file_path(file_path)

        named_temporary_file.assert_called_with(delete=False)
        syrx_file_handler.process_syrx_file.assert_called_with(read_file_mock.__enter__.return_value,
                                                               bad_record_file_mock)

        remove.assert_called_with(file_path)
        bad_record_file_mock.close.assert_called_with()
        move.assert_called_with(bad_record_file_mock.name, file_path)

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_process_syrx_file(self, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.logger = Mock()
        syrx_file_handler.syrx_upload_folder = Mock()
        syrx_file_handler.date_str = Mock()

        bad_record_file_mock = MagicMock()

        summary = ProcessSyrxRecordsReturn()
        summary.num_good_records = 3
        summary.num_bad_records = 1
        syrx_file_handler.process_syrx_records = Mock(return_value=summary)

        read_file_stream = io.StringIO()
        read_file_stream.write(u'{"name": "record0"}\n'
                               u'{"name": "record1"}\n'
                               u'{"name": "record2"}\n'
                               u'{"name": "record3"}')
        read_file_stream.seek(0)

        parsed_list = [{"name": "record0"}, {"name": "record1"}, {"name": "record2"}, {"name": "record3"}]

        rv = syrx_file_handler.process_syrx_file(read_file_stream, bad_record_file_mock)

        syrx_file_handler.process_syrx_records.assert_called_with(parsed_list, bad_record_file_mock)
        assert rv.num_good_records == 3 and rv.num_bad_records == 1

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_process_syrx_file_mass_records(self, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.logger = Mock()
        syrx_file_handler.date_str = Mock()

        bad_record_file_mock = MagicMock()

        summary = ProcessSyrxRecordsReturn()
        summary.num_good_records = 200
        summary.num_bad_records = 0
        syrx_file_handler.process_syrx_records = Mock(return_value=summary)

        read_file_stream = io.StringIO()
        for i in range(400):
            read_file_stream.write(u'{"name": "record"}\n')

        # add extra record to force small batch for good measure
        read_file_stream.write(u'{"name": "record"}')
        read_file_stream.seek(0)

        parsed_list = [{"name": "record"} for i in range(200)]

        rv = syrx_file_handler.process_syrx_file(read_file_stream, bad_record_file_mock)

        syrx_file_handler.process_syrx_records.assert_has_calls([call(parsed_list,  bad_record_file_mock),
                                                                 call(parsed_list, bad_record_file_mock),
                                                                 call([{"name": "record"}], bad_record_file_mock)])
        assert rv.num_good_records == 600

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_equipment_point_records")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.delete_old_records")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.insert_records")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_record_ranges")
    def test_process_johnson_records(self, get_record_ranges, insert_records, delete_old_records,
                                     get_equipment_point_records, uow):
        syrx_file_handler = SyrxFileHandler()

        equipment_point_records = EquipmentPointRecordsReturn()
        equipment_point_records.equipment_point_records = [
            {"name": "record0"},
            {"name": "record1"}
        ]
        equipment_point_records.bad_records = [
            {"name": "record2"},
            {"name": "record3"}
        ]
        get_equipment_point_records.return_value = equipment_point_records

        records = Mock()
        bad_record_file = io.StringIO()

        rv = syrx_file_handler.process_syrx_records(records, bad_record_file)

        get_equipment_point_records.assert_called_with(records)
        delete_old_records.assert_called_with(equipment_point_records.equipment_point_records)
        insert_records.assert_called_with(equipment_point_records.equipment_point_records)

        bad_record_file.seek(0)
        bad_records_written_data = bad_record_file.read().strip().split("\n")
        assert len(bad_records_written_data) == 2
        assert json.loads(bad_records_written_data[0]) == {"name": "record2"}
        assert json.loads(bad_records_written_data[1]) == {"name": "record3"}

        get_record_ranges.assert_called_with(equipment_point_records.equipment_point_records)

        assert rv.num_good_records == 2
        assert rv.num_bad_records == 2
        assert rv.record_ranges == get_record_ranges.return_value

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_weatherstation_years_to_retrieve")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_weather_data_records")
    def test_get_weather_data(self, get_weather_data_records, get_weatherstation_years_to_retrieve, uow):
        syrx_file_handler = SyrxFileHandler()
        records = Mock()

        rv = syrx_file_handler.get_weather_data(records)

        get_weatherstation_years_to_retrieve.assert_called_with(records)
        get_weather_data_records.assert_called_with(get_weatherstation_years_to_retrieve.return_value)
        assert rv == get_weather_data_records.return_value

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_get_weatherstation_years_to_retrieve(self, uow):
        syrx_file_handler = SyrxFileHandler()

        records = [{"weatherstation_id": "ws1", "timestamp": "2014-09-08 13:15"},
                   {"weatherstation_id": "ws1", "timestamp": "2014-10-08 13:15"},
                   {"weatherstation_id": "ws1", "timestamp": "2015-10-08 13:15"},
                   {"weatherstation_id": "ws2", "timestamp": "2015-10-08 13:15"},
                   {"weatherstation_id": "ws3", "timestamp": None}]

        rv = syrx_file_handler.get_weatherstation_years_to_retrieve(records)

        assert rv["ws1"] == {2014, 2015}
        assert rv["ws2"] == {2015}
        assert rv["ws3"] == set()

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_get_weather_data_records(self, uow):
        syrx_file_handler = SyrxFileHandler()

        weatherstation_years_to_retrieve = {"ws1": {2014, 2015}, "ws2": {2015}}
        jan_1_2014 = pytz.utc.localize(datetime.datetime(2014, 1, 1))
        jan_1_2015 = pytz.utc.localize(datetime.datetime(2015, 1, 1))

        def get_noaa_records_side_effect(weatherstation_id, years):
            return [{"weatherstation_id": weatherstation_id,
                     "datetimeutc": pytz.utc.localize(datetime.datetime(y, 1, 1))}
                    for y in years]

        uow.return_value.weather_stations.get_noaa_records.side_effect = get_noaa_records_side_effect

        rv = syrx_file_handler.get_weather_data_records(weatherstation_years_to_retrieve)

        assert rv["ws1"] == {jan_1_2014: {"weatherstation_id": "ws1", "datetimeutc": jan_1_2014},
                             jan_1_2015: {"weatherstation_id": "ws1", "datetimeutc": jan_1_2015}}
        assert rv["ws2"] == {jan_1_2015: {"weatherstation_id": "ws2", "datetimeutc": jan_1_2015}}

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.populate_weatherstation_id_on_records")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_weather_data")
    def test_get_equipment_point_records_successful(self, get_weather_data, populate_weatherstation_id_on_records, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.date_time = Mock()
        syrx_file_handler.date_time_str = Mock()

        weather_data = {"ws1": {pytz.utc.localize(datetime.datetime(2014, 9, 8, 0, 0, 0)): "weather_record_1",
                                pytz.utc.localize(datetime.datetime(2014, 9, 8, 13, 0, 0)): "weather_record_2",
                                pytz.utc.localize(datetime.datetime(2014, 8, 8, 13, 0, 0)): "weather_record_3"}}
        get_weather_data.return_value = weather_data

        records = [{"value": 100, "timestamp": "2014-09-08 00:15:00", "weatherstation_id": "ws1", "syrx_num": "400000-0001-237323-EP-001"},
                   {"value": 100, "timestamp": "2014-09-08 13:00:00", "weatherstation_id": "ws1", "syrx_num": "400000-0001-237323-EP-001"},
                   {"value": 100, "timestamp": "2014-08-08 13:00:00", "weatherstation_id": "ws1", "syrx_num": "400000-0001-237323-EP-001"}]

        rv = syrx_file_handler.get_equipment_point_records(records)

        populate_weatherstation_id_on_records.assert_called_with(records)
        get_weather_data.assert_called_with(records)

        assert len(rv.equipment_point_records) == 3
        assert len(rv.bad_records) == 0

        uow.return_value.energy_records.get_equipment_point_record.assert_has_calls([
            call(pytz.utc.localize(datetime.datetime(2014, 9, 8, 0, 15, 0)), "400000-0001-237323-EP-001", 100,
                 "weather_record_1", syrx_file_handler.date_time),
            call(pytz.utc.localize(datetime.datetime(2014, 9, 8, 13, 0, 0)), "400000-0001-237323-EP-001", 100,
                 "weather_record_2", syrx_file_handler.date_time),
            call(pytz.utc.localize(datetime.datetime(2014, 8, 8, 13, 0, 0)), "400000-0001-237323-EP-001", 100,
                 "weather_record_3", syrx_file_handler.date_time)

        ])

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.populate_weatherstation_id_on_records")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_weather_data")
    def test_get_equipment_point_records_invalid_number(self, get_weather_data, populate_weatherstation_id_on_records, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.date_time = Mock()
        syrx_file_handler.date_time_str = Mock()

        weather_data = {"ws1": {pytz.utc.localize(datetime.datetime(2014, 9, 8, 0, 0, 0)): "weather_record_1"}}
        get_weather_data.return_value = weather_data

        records = [{"value": "x", "timestamp": "2014-09-08 00:15:00", "weatherstation_id": "ws1", "syrx_num": "400000-0001-237323-EP-001"}]

        rv = syrx_file_handler.get_equipment_point_records(records)

        populate_weatherstation_id_on_records.assert_called_with(records)
        get_weather_data.assert_called_with(records)

        assert len(rv.equipment_point_records) == 0
        assert len(rv.bad_records) == 1

        assert rv.bad_records[0] == {"value": "x", "timestamp": "2014-09-08 00:15:00", "weatherstation_id": "ws1",
                                     "syrx_num": "400000-0001-237323-EP-001",
                                     "error": {"date": syrx_file_handler.date_time_str,
                                               "messages": ["Value is not a number"]}}

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.populate_weatherstation_id_on_records")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_weather_data")
    def test_get_equipment_point_records_invalid_timestamp(self, get_weather_data, populate_weatherstation_id_on_records, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.date_time = Mock()
        syrx_file_handler.date_time_str = Mock()

        weather_data = {"ws1": {pytz.utc.localize(datetime.datetime(2014, 9, 8, 0, 0, 0)): "weather_record_1"}}
        get_weather_data.return_value = weather_data

        records = [{"value": 100, "timestamp": "x", "weatherstation_id": "ws1", "syrx_num": "400000-0001-237323-EP-001"}]

        rv = syrx_file_handler.get_equipment_point_records(records)

        populate_weatherstation_id_on_records.assert_called_with(records)
        get_weather_data.assert_called_with(records)

        assert len(rv.equipment_point_records) == 0
        assert len(rv.bad_records) == 1

        assert rv.bad_records[0] == {"value": 100, "timestamp": "x", "weatherstation_id": "ws1",
                                     "syrx_num": "400000-0001-237323-EP-001",
                                     "error": {"date": syrx_file_handler.date_time_str,
                                               "messages": ["Timestamp could not be parsed"]}}

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.populate_weatherstation_id_on_records")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_weather_data")
    def test_get_equipment_point_records_missing_weatherstation(self, get_weather_data, populate_weatherstation_id_on_records, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.date_time = Mock()
        syrx_file_handler.date_time_str = Mock()

        weather_data = {"ws1": {pytz.utc.localize(datetime.datetime(2014, 9, 8, 0, 0, 0)): "weather_record_1"}}
        get_weather_data.return_value = weather_data

        records = [{"value": 100, "timestamp": "2014-09-08 00:15:00", "syrx_num": "400000-0001-237323-EP-001"}]

        rv = syrx_file_handler.get_equipment_point_records(records)

        populate_weatherstation_id_on_records.assert_called_with(records)
        get_weather_data.assert_called_with(records)

        assert len(rv.equipment_point_records) == 0
        assert len(rv.bad_records) == 1

        assert rv.bad_records[0] == {"value": 100, "timestamp": "2014-09-08 00:15:00",
                                     "syrx_num": "400000-0001-237323-EP-001",
                                     "error": {"date": syrx_file_handler.date_time_str,
                                               "messages": ["Weatherstation not found"]}}

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.populate_weatherstation_id_on_records")
    @patch("vendor_data_pipeline.syrx_file_handler.SyrxFileHandler.get_weather_data")
    def test_get_equipment_point_records_missing_weather_data(self, get_weather_data, populate_weatherstation_id_on_records, uow):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.date_time = Mock()
        syrx_file_handler.date_time_str = Mock()

        weather_data = {"ws1": {pytz.utc.localize(datetime.datetime(2014, 8, 8, 0, 0, 0)): "weather_record_1"}}
        get_weather_data.return_value = weather_data

        records = [{"value": 100, "timestamp": "2014-09-08 00:15:00", "weatherstation_id": "ws1", "syrx_num": "400000-0001-237323-EP-001"}]

        rv = syrx_file_handler.get_equipment_point_records(records)

        populate_weatherstation_id_on_records.assert_called_with(records)
        get_weather_data.assert_called_with(records)

        assert len(rv.equipment_point_records) == 0
        assert len(rv.bad_records) == 1

        assert rv.bad_records[0] == {"value": 100, "timestamp": "2014-09-08 00:15:00", "weatherstation_id": "ws1",
                                     "syrx_num": "400000-0001-237323-EP-001",
                                     "error": {"date": syrx_file_handler.date_time_str,
                                               "messages": ['Time 2014-09-08 00:00:00 not found in weather data']}}

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_delete_old_record(self, uow):
        syrx_file_handler = SyrxFileHandler()

        records = [{"syrx_num": "syrx_num_1", "date": "date_1"},
                   {"syrx_num": "syrx_num_2", "date": "date_2"},
                   {"syrx_num": "syrx_num_3", "date": "date_3"}]

        record_keys = [[r["syrx_num"], r["date"]] for r in records]

        syrx_file_handler.delete_old_records(records)

        uow.return_value.energy_records.delete_equipment_point_records.assert_called_with(record_keys)

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_insert_record(self, uow):
        syrx_file_handler = SyrxFileHandler()
        records = Mock()

        syrx_file_handler.insert_records(records)

        uow.return_value.energy_records.insert_equipment_point_records.assert_called_with(records)

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_get_record_ranges(self, uow):
        syrx_file_handler = SyrxFileHandler()

        records = [{"syrx_num": "syrx_num_1", "date": datetime.datetime(2012, 1, 1)},
                   {"syrx_num": "syrx_num_1", "date": datetime.datetime(2012, 2, 1)},
                   {"syrx_num": "syrx_num_1", "date": datetime.datetime(2012, 3, 1)},
                   {"syrx_num": "syrx_num_2", "date": datetime.datetime(2012, 2, 1)},
                   {"syrx_num": "syrx_num_2", "date": datetime.datetime(2012, 3, 1)}]

        rv = syrx_file_handler.get_record_ranges(records)

        assert rv[0].syrx_num == "syrx_num_1"
        assert rv[0].start_date == datetime.datetime(2012, 1, 1)
        assert rv[0].end_date == datetime.datetime(2012, 3, 1)

        assert rv[1].syrx_num == "syrx_num_2"
        assert rv[1].start_date == datetime.datetime(2012, 2, 1)
        assert rv[1].end_date == datetime.datetime(2012, 3, 1)

    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    @patch("vendor_data_pipeline.syrx_file_handler.EnergyRecordCompiler")
    def test_compile_equipment_point_records(self, energy_record_compiler, uow):
        syrx_file_handler = SyrxFileHandler()

        range1 = RecordRange()
        range1.syrx_num = "syrx_num_1"
        range1.start_date = datetime.datetime(2012, 1, 1)
        range1.end_date = datetime.datetime(2012, 3, 1)
        range2 = RecordRange()
        range2.syrx_num = "syrx_num_2"
        range2.start_date = datetime.datetime(2012, 2, 1)
        range2.end_date = datetime.datetime(2012, 3, 1)
        ranges = [range1, range2]

        syrx_file_handler.compile_equipment_point_records(ranges)

        compiler = energy_record_compiler.return_value

        uow.return_value.compiled_energy_records.delete_compiled_equipment_point_records\
            .assert_has_calls([call(range1.syrx_num, range1.start_date, range1.end_date),
                               call(range2.syrx_num, range2.start_date, range2.end_date)])

        compiler.compile_component_point_records_by_year_span\
            .assert_has_calls([call(range1.syrx_num, range1.start_date, range1.end_date),
                               call(range2.syrx_num, range2.start_date, range2.end_date)])


    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_flatten_record_ranges(self, uow):
        syrx_file_handler = SyrxFileHandler()

        records = [RecordRange("syrx_num_1", datetime.datetime(2012, 1, 1), datetime.datetime(2012, 3, 1)),
                   RecordRange("syrx_num_1", datetime.datetime(2012, 4, 1), datetime.datetime(2012, 6, 1)),
                   RecordRange("syrx_num_2", datetime.datetime(2012, 7, 1), datetime.datetime(2012, 9, 1)),
                   RecordRange("syrx_num_2", datetime.datetime(2012, 10, 1), datetime.datetime(2012, 12, 1))]

        rv = syrx_file_handler.flatten_record_ranges(records)

        assert rv[0].syrx_num == "syrx_num_1"
        assert rv[0].start_date == datetime.datetime(2012, 1, 1)
        assert rv[0].end_date == datetime.datetime(2012, 6, 1)

        assert rv[1].syrx_num == "syrx_num_2"
        assert rv[1].start_date == datetime.datetime(2012, 7, 1)
        assert rv[1].end_date == datetime.datetime(2012, 12, 1)


    @patch("vendor_data_pipeline.syrx_file_handler.UoW")
    def test_get_unique_syrx_nums(self, uow):
        syrx_file_handler = SyrxFileHandler()

        records = [{"syrx_num": "syrx_num_1"}, {"syrx_num": "syrx_num_1"}, {"syrx_num": "syrx_num_2"}]

        rv = syrx_file_handler.get_unique_syrx_nums(records)

        assert rv == ["syrx_num_1", "syrx_num_2"]