import csv
import datetime
import json
import threading
import os
import pytz
from db.uow import UoW
from dateutil.parser import parse

class PostHandler:

    def __init__(self):
        self.run_timestamp = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        self.uow = UoW(None)

    def handle_johnson_post(self, csv_records):
        # as of 2015-09-25, johnson's data uses local time

        reader = csv.reader(csv_records)
        db_records = []

        imported_points = []

        for csv_record in reader:
            # first row is a header row
            if reader.line_num == 1:
                continue

            if not isinstance(csv_record, list) or len(csv_record) < 5:
                continue

            site_id = str(csv_record[0])
            fqr = str(csv_record[1])
            local_timestamp = datetime.datetime.strptime(csv_record[2], '%m/%d/%Y %I:%M %p')\
                .replace(tzinfo=pytz.timezone("US/Eastern"))

            utc_timestamp = local_timestamp.astimezone(pytz.UTC)
            value = csv_record[3]
            reliability = csv_record[4]

            sensor_id = "johnson|{site_id}|{fqr}".format(site_id=site_id, fqr=fqr)

            db_records.append({
                "vendor": "johnson",
                "sensor_id": sensor_id,
                "johnson_site_id": site_id,
                "johnson_fqr": fqr,
                "johnson_reliability": reliability,
                "hours_in_record": 0.25,
                "local_year": local_timestamp.year,
                "local_month": local_timestamp.month,
                "local_hour": local_timestamp.hour,
                "local_day_of_month": local_timestamp.day,
                "local_timestamp": local_timestamp,
                "utc_timestamp": utc_timestamp,
                "value": str(value),
                "date_added": self.run_timestamp
            })
            imported_points.append({"id": sensor_id, "johnson_site_id": site_id, "sensor_id": sensor_id,
                                    "johnson_fqr": fqr, "vendor": "johnson"})

        self.uow.vendor_records.insert_vendor_records(db_records)
        self.uow.vendor_records.insert_fieldserver_points(imported_points)

    def handle_fieldserver_post(self, data):
        utc_time = round_time(datetime.datetime.now(pytz.UTC))
        local_time = utc_time.astimezone(pytz.timezone("US/Eastern"))
        records = []

        imported_points = []

        # fieldserver posted data looks like this:
        # cc14153300_Offsets_0320-0359=1.000,1.000,1.000,....
        # this comes in as a data dictionary with one element, that element's key is cc14153300_Offsets_0320-0359
        # and the value is the comma separated list of values

        for (key, values) in data.iteritems():
            key_split = key.split("_")
            if len(key_split) >= 3 and key_split[1] == "Offsets":
                site_id = key_split[0]
                starting_offset = int(key_split[2].split("-")[0])
                values_array = values.split(",")
                for index, value in enumerate(values_array):
                    offset = starting_offset + index
                    sensor_id = "fieldserver|{site_id}|{offset}".format(site_id=site_id, offset=offset)

                    records.append({
                        "vendor": "fieldserver",
                        "sensor_id": sensor_id,
                        "fieldserver_site_id": site_id,
                        "fieldserver_offset": offset,
                        "hours_in_record": 0.25,
                        "local_year": local_time.year,
                        "local_month": local_time.month,
                        "local_hour": local_time.hour,
                        "local_day_of_month": local_time.day,
                        "local_timestamp": local_time,
                        "utc_timestamp": utc_time,
                        "value": str(value.strip()),
                        "date_added": self.run_timestamp
                    })
                    imported_points.append({"id": sensor_id, "fieldserver_site_id": site_id, "sensor_id": sensor_id,
                                            "fieldserver_offset": offset, "vendor": "fieldserver"})

        self.uow.vendor_records.insert_vendor_records(records)
        self.uow.vendor_records.insert_fieldserver_points(imported_points)

    def handle_invensys_post(self, csv_records):
        reader = csv.reader(csv_records)
        db_records = []

        imported_points = []

        for row in reader:
            if not isinstance(row, list) or len(row) < 5:
                continue

            local_timestamp = parse(str(row[0]))
            utc_timestamp = local_timestamp.astimezone(pytz.utc)
            site_name = str(row[1])
            equipment_name = str(row[2])
            point_name = str(row[3])
            value = str(row[4])

            sensor_id = "invensys|{site_name}|{equipment_name}|{point_name}".format(site_name=site_name,
                                                                                    equipment_name=equipment_name,
                                                                                    point_name=point_name)

            db_records.append({
                "vendor": "invensys",
                "sensor_id": sensor_id,
                "invensys_site_name": site_name,
                "invensys_equipment_name": equipment_name,
                "invensys_point_name": point_name,
                "hours_in_record": 0.25,
                "local_year": local_timestamp.year,
                "local_month": local_timestamp.month,
                "local_hour": local_timestamp.hour,
                "local_day_of_month": local_timestamp.day,
                "local_timestamp": local_timestamp,
                "utc_timestamp": utc_timestamp,
                "value": value,
                "date_added": self.run_timestamp
            })
            imported_points.append({"id": sensor_id, "vendor": "johnson", "invensys_site_name": site_name,
                                    "invensys_equipment_name": equipment_name, "invensys_point_name": point_name,
                                    "sensor_id": sensor_id})

        self.uow.vendor_records.insert_vendor_records(db_records)
        self.uow.vendor_records.insert_invensys_points(imported_points)

    def handle_invensys_form_post(self, data):
        db_records = []

        imported_points = []

        for (key, value) in data.iteritems():
            for row in key.splitlines():
                row_data = row.split(",")

                if not isinstance(row_data, list) or len(row_data) < 5:
                    continue

                local_timestamp = parse(str(row_data[0]))
                utc_timestamp = local_timestamp.astimezone(pytz.utc)
                site_name = str(row_data[1])
                equipment_name = str(row_data[2])
                point_name = str(row_data[3])
                value = str(row_data[4])

                sensor_id = "invensys|{site_name}|{equipment_name}|{point_name}".format(site_name=site_name,
                                                                                        equipment_name=equipment_name,
                                                                                        point_name=point_name)

                db_records.append({
                    "vendor": "invensys",
                    "sensor_id": sensor_id,
                    "invensys_site_name": site_name,
                    "invensys_equipment_name": equipment_name,
                    "invensys_point_name": point_name,
                    "hours_in_record": 0.25,
                    "local_year": local_timestamp.year,
                    "local_month": local_timestamp.month,
                    "local_hour": local_timestamp.hour,
                    "local_day_of_month": local_timestamp.day,
                    "local_timestamp": local_timestamp,
                    "utc_timestamp": utc_timestamp,
                    "value": value,
                    "date_added": self.run_timestamp
                })
                imported_points.append({"id": sensor_id, "vendor": "invensys", "invensys_site_name": site_name,
                                        "invensys_equipment_name": equipment_name, "invensys_point_name": point_name,
                                        "sensor_id": sensor_id})

        self.uow.vendor_records.insert_vendor_records(db_records)
        self.uow.vendor_records.insert_invensys_points(imported_points)


def round_time(time):
    minute = time.minute
    minute_remainder = minute % 15
    new_time = datetime.datetime(time.year, time.month, time.day, time.hour, 0, 0).replace(tzinfo=pytz.UTC)

    if minute_remainder < 7 or (minute_remainder == 7 and time.second < 30):
        minute -= minute_remainder
    else:
        minute = minute - minute_remainder + 15

    new_time += datetime.timedelta(seconds=minute*60)

    return new_time
