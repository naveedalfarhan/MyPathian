import unittest
import datetime
from db.repositories.energy_record_repository import EnergyRecordRepository
from mock import Mock, patch, MagicMock
import pytz


class TestEnergyRecordRepository(unittest.TestCase):
    def test_get_equipment_point_record_offpeak1(self):
        date = pytz.UTC.localize(datetime.datetime(2014, 1, 1, 0, 0, 0))
        syrx_num = Mock()
        value = Mock()
        weather = Mock()
        created_on = Mock()

        record = EnergyRecordRepository.get_equipment_point_record(date, syrx_num, value, weather, created_on)

        self.assertDictEqual(record, {
            "created_on": created_on,
            "date": date,
            "hours_in_record": 0.25,
            "local_day_of_month": date.day,
            "local_day_of_week": date.weekday(),
            "local_hour": date.hour,
            "local_month": date.month,
            "local_year": date.year,
            "syrx_num": syrx_num,
            "value": value,
            "weather": weather,
            "peak": "offpeak"
        })

    def test_get_equipment_point_record_offpeak2(self):
        date = pytz.UTC.localize(datetime.datetime(2014, 7, 5, 15, 0, 0))
        syrx_num = Mock()
        value = Mock()
        weather = Mock()
        created_on = Mock()

        record = EnergyRecordRepository.get_equipment_point_record(date, syrx_num, value, weather, created_on)

        self.assertDictEqual(record, {
            "created_on": created_on,
            "date": date,
            "hours_in_record": 0.25,
            "local_day_of_month": date.day,
            "local_day_of_week": date.weekday(),
            "local_hour": date.hour,
            "local_month": date.month,
            "local_year": date.year,
            "syrx_num": syrx_num,
            "value": value,
            "weather": weather,
            "peak": "offpeak"
        })

    def test_get_equipment_point_record_offpeak3(self):
        date = pytz.UTC.localize(datetime.datetime(2014, 7, 1, 0, 0, 0))
        syrx_num = Mock()
        value = Mock()
        weather = Mock()
        created_on = Mock()

        record = EnergyRecordRepository.get_equipment_point_record(date, syrx_num, value, weather, created_on)

        self.assertDictEqual(record, {
            "created_on": created_on,
            "date": date,
            "hours_in_record": 0.25,
            "local_day_of_month": date.day,
            "local_day_of_week": date.weekday(),
            "local_hour": date.hour,
            "local_month": date.month,
            "local_year": date.year,
            "syrx_num": syrx_num,
            "value": value,
            "weather": weather,
            "peak": "offpeak"
        })

    def test_get_equipment_point_record_peak(self):
        date = pytz.UTC.localize(datetime.datetime(2014, 7, 1, 13, 0, 0))
        syrx_num = Mock()
        value = Mock()
        weather = Mock()
        created_on = Mock()

        record = EnergyRecordRepository.get_equipment_point_record(date, syrx_num, value, weather, created_on)

        self.assertDictEqual(record, {
            "created_on": created_on,
            "date": date,
            "hours_in_record": 0.25,
            "local_day_of_month": date.day,
            "local_day_of_week": date.weekday(),
            "local_hour": date.hour,
            "local_month": date.month,
            "local_year": date.year,
            "syrx_num": syrx_num,
            "value": value,
            "weather": weather,
            "peak": "peak"
        })