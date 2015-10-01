import rethinkdb as r
import datetime
import pytz
from itertools import groupby


"""
{
    "created_on": Fri Jan 30 2015 23:41:02 GMT+00:00 ,
    "date": Sat Dec 13 2014 06:15:00 GMT+00:00 ,
    "hours_in_record": 0.25 ,
    "id":  "00001231-5ec4-459e-918b-437f48bd7e17" ,
    "local_day_of_month": 13 ,
    "local_day_of_week": 5 ,
    "local_hour": 6 ,
    "local_month": 12 ,
    "local_year": 2014 ,
    "peak":  "offpeak" ,
    "syrx_num":  "330938-52-233416002003005-BP-2" ,
    "value": 1 ,
    "weather": {
        "alt": 30.32 ,
        "alt_guess": false ,
        "datetimeutc": Sat Dec 13 2014 06:00:00 GMT+00:00 ,
        "dewpt": 33 ,
        "dewpt_guess": false ,
        "enthalpy": 12.6 ,
        "enthalpy_guess": false ,
        "id":  "90349dab-7d15-4b29-9809-4d6f3ee70d9e" ,
        "localyear": 2014 ,
        "temp": 36 ,
        "temp_guess": false ,
        "weatherstation_id":  "7f931d5e-1efa-4650-bfd7-4e2ca12aebf4"
    }
}
"""
report_execution_date = datetime.datetime.now(pytz.UTC)

weatherstation_id = "ec8a9688-29a3-4a51-bd94-7d2b0a7f85a4"
year = 2014
syrx_num = "1-1-237323001-EP-34"


db_conn = r.connect()

weather_records = list(r.db("pathian").table("noaarecords")
                       .get_all([weatherstation_id, year], index="weatherstation_year")
                       .order_by("datetimeutc")
                       .run(db_conn))
grouped_weather_records = dict()
for k, v in groupby(weather_records, lambda x: x["datetimeutc"]):
    grouped_weather_records[k] = list(v)[0]

current_date = datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)

equipment_point_record_buffer_length = 0
equipment_point_record_buffer = []

current_record = 0
while current_date.year == year:
    rounded_date = datetime.datetime(current_date.year, current_date.month, current_date.day, current_date.hour, tzinfo=pytz.UTC)
    try:
        weather_record = grouped_weather_records[rounded_date]
    except:
        current_date += datetime.timedelta(minutes=15)
        continue

    equipment_point_record = {
        "created_on": report_execution_date,
        "date": current_date,
        "hours_in_record": 0.25,
        "local_day_of_month": current_date.day,
        "local_day_of_week": current_date.weekday(),
        "local_hour": current_date.hour,
        "local_month": current_date.month,
        "local_year": current_date.year,
        "peak":  "offpeak",
        "syrx_num":  syrx_num,
        "value": weather_record["temp"] / 2,
        "weather": weather_record
    }
    equipment_point_record_buffer.append(equipment_point_record)
    equipment_point_record_buffer_length += 1

    if equipment_point_record_buffer_length >= 200:
        current_record += equipment_point_record_buffer_length
        print("processed " + str(current_record) + " records")
        r.db("pathian").table("equipment_point_records").insert(equipment_point_record_buffer).run(db_conn)
        equipment_point_record_buffer = []
        equipment_point_record_buffer_length = 0

    current_date += datetime.timedelta(minutes=15)


if equipment_point_record_buffer_length > 0:
    r.db("pathian").table("equipment_point_records").insert(equipment_point_record_buffer)
    equipment_point_record_buffer = []
    equipment_point_record_buffer_length = 0