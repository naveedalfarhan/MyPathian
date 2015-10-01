import json
import unittest
import io
import datetime
from mock import Mock, MagicMock, patch
import pytz
from vendor_data_pipeline.post_handler import PostHandler, round_time



class TestPostHandler(unittest.TestCase):
    @patch("vendor_data_pipeline.post_handler.os.path.join")
    @patch("vendor_data_pipeline.post_handler.open", create=True)
    def test_handle_johnson_post(self, open_mock, path_join):
        file_mock = MagicMock()

        post_handler = PostHandler()
        post_handler.write_johnson_post_data = Mock()
        post_handler.johnson_raw_folder = Mock()
        post_handler.handle_johnson_post(file_mock)

        path_join.assert_called_with(post_handler.johnson_raw_folder, post_handler.date_str)
        open_mock.assert_called_with(path_join.return_value, "a")
        post_handler.write_johnson_post_data.assert_called_with(file_mock,
                                                                open_mock.return_value.__enter__.return_value)


    def test_write_johnson_post_data(self):
        source_stream = io.StringIO()
        destination_stream = io.StringIO()

        source_stream.write(u"Site ID, FQR, Timestamp, Value, Reliability\n"
                            u"123456,ABC,2012-01-01 12:00 AM,100,Reliable\n"
                            u"123457,DEF,2012-01-01 12:15 AM,200,Unreliable")

        source_stream.seek(0)

        post_handler = PostHandler()
        post_handler.date_time_str = "2014-09-06 16:45:00"
        post_handler.write_johnson_post_data(source_stream, destination_stream)

        destination_stream.seek(0)
        written_data = destination_stream.read().strip().split("\n")

        assert len(written_data) == 2
        row0 = json.loads(written_data[0])
        row1 = json.loads(written_data[1])
        assert row0 == {"site_id": "123456", "fqr": "ABC", "timestamp": "2012-01-01 12:00 AM", "value": "100",
                        "reliability": "Reliable", "date_added": "2014-09-06 16:45:00"}
        assert row1 == {"site_id": "123457", "fqr": "DEF", "timestamp": "2012-01-01 12:15 AM", "value": "200",
                        "reliability": "Unreliable", "date_added": "2014-09-06 16:45:00"}

    @patch("vendor_data_pipeline.post_handler.os.path.join")
    @patch("vendor_data_pipeline.post_handler.open", create=True)
    def test_handle_fieldserver_post(self, open_mock, path_join):
        data_mock = MagicMock()

        post_handler = PostHandler()
        post_handler.write_fieldserver_post_data = Mock()
        post_handler.fieldserver_raw_folder = Mock()
        post_handler.handle_fieldserver_post(data_mock)

        path_join.assert_called_with(post_handler.fieldserver_raw_folder, post_handler.date_str)
        open_mock.assert_called_with(path_join.return_value, "a")
        post_handler.write_fieldserver_post_data.assert_called_with(data_mock,
                                                                    open_mock.return_value.__enter__.return_value)

    @patch("vendor_data_pipeline.post_handler.round_time")
    def test_write_fieldserver_post_data(self, round_time):
        post_handler = PostHandler()
        post_handler.date_time_str = "2014-09-06 16:45:00"
        round_time.return_value = pytz.utc.localize(datetime.datetime(2014, 9, 5))

        data = {"cc14153300_Offsets_0000-0009": "44.000000 ,44.5 ,45 ,45.5 ,46 ,46.5 ,47 ,47.5 ,48 ,48.5"}
        destination_stream = io.StringIO()

        post_handler.write_fieldserver_post_data(data, destination_stream)

        destination_stream.seek(0)
        written_data = destination_stream.read().strip().split("\n")

        assert len(written_data) == 10
        assert json.loads(written_data[0]) == {"site_id": "cc14153300", "offset": 0, "value": "44.000000",
                                               "timestamp": "2014-09-05 00:00:00", "date_added": post_handler.date_time_str}
        assert json.loads(written_data[1]) == {"site_id": "cc14153300", "offset": 1, "value": "44.5",
                                               "timestamp": "2014-09-05 00:00:00", "date_added": post_handler.date_time_str}

    @patch("vendor_data_pipeline.post_handler.round_time")
    def test_write_fieldserver_post_data_with_offset(self, round_time):
        post_handler = PostHandler()
        post_handler.date_time_str = "2014-09-06 16:45:00"
        round_time.return_value = pytz.utc.localize(datetime.datetime(2014, 9, 5))

        data = {"cc14153300_Offsets_0010-0019": "44.000000 ,44.5 ,45 ,45.5 ,46 ,46.5 ,47 ,47.5 ,48 ,48.5"}
        destination_stream = io.StringIO()

        post_handler.write_fieldserver_post_data(data, destination_stream)

        destination_stream.seek(0)
        written_data = destination_stream.read().strip().split("\n")

        assert len(written_data) == 10
        assert json.loads(written_data[0]) == {"site_id": "cc14153300", "offset": 10, "value": "44.000000",
                                               "timestamp": "2014-09-05 00:00:00", "date_added": post_handler.date_time_str}
        assert json.loads(written_data[1]) == {"site_id": "cc14153300", "offset": 11, "value": "44.5",
                                               "timestamp": "2014-09-05 00:00:00", "date_added": post_handler.date_time_str}


    @patch("vendor_data_pipeline.post_handler.os.path.join")
    @patch("vendor_data_pipeline.post_handler.open", create=True)
    def test_handle_invensys_post(self, open_mock, path_join):
        file_mock = MagicMock()

        post_handler = PostHandler()
        post_handler.write_invensys_post_data = Mock()
        post_handler.invensys_raw_folder = Mock()

        post_handler.handle_invensys_post(file_mock)

        path_join.assert_called_with(post_handler.invensys_raw_folder, post_handler.date_str)
        open_mock.assert_called_with(path_join.return_value, "a")
        post_handler.write_invensys_post_data.assert_called_with(file_mock,
                                                                 open_mock.return_value.__enter__.return_value)


    def test_write_invensys_post_data(self):
        source_stream = io.StringIO()
        destination_stream = io.StringIO()

        source_stream.write(u"2014-07-10T11:00:00.241-04:00,Bethesda Oak,Towers,WestTower_1A_VFD%_ID905,100.0\n"
                            u"2014-07-10T11:00:00.241-04:00,Bethesda Oak,Towers,WestTower_1B_VFD%_ID906,100.0\n"
                            u"2014-07-10T11:00:00.241-04:00,Bethesda Oak,Towers,EastTower_2A_VFD%_ID661,100.0\n"
                            u"2014-07-10T11:00:00.241-04:00,Bethesda Oak,Towers,EastTower_2B_VFD%_ID662,100.0")

        source_stream.seek(0)

        post_handler = PostHandler()
        post_handler.date_time_str = "2014-09-06 16:45:00"
        post_handler.write_invensys_post_data(source_stream, destination_stream)

        destination_stream.seek(0)
        written_data = destination_stream.read().strip().split("\n")

        assert len(written_data) == 4
        row0 = json.loads(written_data[0])
        row1 = json.loads(written_data[1])
        row2 = json.loads(written_data[2])
        row3 = json.loads(written_data[3])
        assert row0 == {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Bethesda Oak",
                        "invensys_equipment_name": "Towers", "invensys_point_name": "WestTower_1A_VFD%_ID905",
                        "value": "100.0", "date_added": "2014-09-06 16:45:00"}
        assert row1 == {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Bethesda Oak",
                        "invensys_equipment_name": "Towers", "invensys_point_name": "WestTower_1B_VFD%_ID906",
                        "value": "100.0", "date_added": "2014-09-06 16:45:00"}
        assert row2 == {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Bethesda Oak",
                        "invensys_equipment_name": "Towers", "invensys_point_name": "EastTower_2A_VFD%_ID661",
                        "value": "100.0", "date_added": "2014-09-06 16:45:00"}
        assert row3 == {"timestamp": "2014-07-10T11:00:00.241-04:00", "invensys_site_name": "Bethesda Oak",
                        "invensys_equipment_name": "Towers", "invensys_point_name": "EastTower_2B_VFD%_ID662",
                        "value": "100.0", "date_added": "2014-09-06 16:45:00"}

    def test_round_time_to_nearest_quarter_hour(self):

        time = pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 0, 0))
        assert round_time(time) == pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 0, 0))

        time = pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 6, 0))
        assert round_time(time) == pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 0, 0))

        time = pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 7, 0))
        assert round_time(time) == pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 0, 0))

        time = pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 8, 0))
        assert round_time(time) == pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 15, 0))

        time = pytz.utc.localize(datetime.datetime(2014, 1, 1, 0, 59, 0))
        assert round_time(time) == pytz.utc.localize(datetime.datetime(2014, 1, 1, 1, 0, 0))

        time = pytz.utc.localize(datetime.datetime(2014, 1, 31, 23, 59, 0))
        assert round_time(time) == pytz.utc.localize(datetime.datetime(2014, 2, 1, 0, 0, 0))

        time = pytz.utc.localize(datetime.datetime(2014, 12, 31, 23, 59, 0))
        assert round_time(time) == pytz.utc.localize(datetime.datetime(2015, 1, 1, 0, 0, 0))