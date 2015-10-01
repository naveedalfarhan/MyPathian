from datetime import datetime, timedelta, tzinfo
from db.uow import UoW
import pytz
import random

def date_range_generator(start, end, delta):
    d = start
    while d < end:
        yield d
        d += delta

def import_data():
    uow = UoW(False)

    # syrx_num, date, value
    # 346643-8-233313-EP-1

    fifteen_min = timedelta(minutes=15)
    start_date = datetime(2005, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
    end_date = datetime(2006, 1, 1, 0, 0, 0, tzinfo=pytz.utc)


    weather_records = uow.weather_stations.get_noaa_records("f443910c-6178-483e-bcf3-9a53299b1196", [2012])
    weather_records_dict = dict((v["datetimeutc"].isoformat(), v) for v in weather_records)

    num_imported = 0
    buffer_list = []
    for d in date_range_generator(start_date, end_date, fifteen_min):
        try:
            rounded_date_time = d + timedelta(0, 0, minutes=d.minute * -1)
            weather = weather_records_dict[rounded_date_time.isoformat()]
            record = {
                "date": d,
                "local_year": d.year,
                "local_month": d.month,
                "local_day_of_week": d.isoweekday(),
                "local_hour": d.hour,
                "hours_in_record": 0.25,
                "syrx_num": "400000-16-237323-EP-001",
                "value": weather["temp"] + 20,
                "weather": weather,
                "peak": False
            }
            buffer_list.append(record)

            if len(buffer_list) == 500:
                uow.energy_records.insert_equipment_point_records(buffer_list)
                num_imported += 500
                print(str(num_imported) + " imported")
                buffer_list = []
        except:
            pass

    if len(buffer_list) > 0:
        uow.energy_records.insert_equipment_point_records(buffer_list)
        num_imported += len(buffer_list)
        print(str(num_imported) + " imported")
        buffer_list = []


    #uow.energy_records.insert_equipment_point_records(buffer_list)


if __name__ == "__main__":
    import_data()