from collections import defaultdict
import datetime
from itertools import groupby
import json
from shutil import move
from tempfile import NamedTemporaryFile
from compile_energy_records import EnergyRecordCompiler
import dateutil.parser
from db.uow import UoW
from os import listdir, path, remove
import pytz

class RecordRange:
    def __init__(self, syrx_num=None, start_date=None, end_date=None):
        self.syrx_num = syrx_num
        self.start_date = start_date
        self.end_date = end_date

class ProcessSyrxRecordsReturn:
    def __init__(self):
        self.num_good_records = 0
        self.num_bad_records = 0
        self.record_ranges = []

class EquipmentPointRecordsReturn:
    def __init__(self):
        self.equipment_point_records = []
        self.bad_records = []

class SyrxFileHandler:
    def __init__(self):
        self.syrx_upload_folder = None
        self.logger = None
        self.uow = UoW(None)

        self.date_time = pytz.utc.localize(datetime.datetime.utcnow())
        self.date_time_str = self.date_time.strftime("%Y-%m-%d %H:%M:%S")

    def process_all_syrx_files(self):
        record_ranges = []
        file_names = listdir(self.syrx_upload_folder)
        self.logger.debug("Found " + str(len(file_names)) + " syrx file(s) to process")

        file_count = len(file_names)
        for i, file_name in enumerate(file_names):
            record_ranges += self.process_syrx_filename(i, file_name, file_count)

        self.compile_equipment_point_records(record_ranges)
        self.logger.debug("Finished importing syrx files")

    def process_syrx_filename(self, index, file_name, file_count):
        self.logger.debug("Importing file " + str(index + 1) + "/" + str(file_count))
        file_path = path.join(self.syrx_upload_folder, file_name)
        self.logger.debug("File path: " + file_path)

        try:
            record_ranges = self.process_syrx_file_path(file_path)
            return record_ranges
        except:
            self.logger.exception("An error occurred importing syrx file located at " + file_path)
            return []

    def process_syrx_file_path(self, file_path):

        bad_record_file = NamedTemporaryFile(delete=False)

        with open(file_path, "r") as f:
            summary = self.process_syrx_file(f, bad_record_file)

        remove(file_path)

        bad_record_file.close()
        if summary.num_bad_records == 0:
            remove(bad_record_file.name)
        else:
            move(bad_record_file.name, file_path)

        self.logger.debug("Found " + str(summary.num_good_records) + " good record(s)")
        self.logger.debug("Found " + str(summary.num_bad_records) + " bad record(s)")

        flat_ranges = self.flatten_record_ranges(summary.record_ranges)

        return flat_ranges

    def process_syrx_file(self, read_file, bad_record_file):
        rv = ProcessSyrxRecordsReturn()

        records = []
        line_count = 0
        for line in read_file:
            line_count += 1

        read_file.seek(0)

        self.logger.debug("Found " + str(line_count) + " lines")

        line_no = 0
        last_processed = 0
        for line in read_file:
            r = json.loads(line)
            records.append(r)
            line_no += 1

            if len(records) % 200 == 0 or line_no == line_count:
                self.logger.debug("Processing lines " + str(last_processed + 1) + "-" +
                                  str(last_processed + 200) + " of " + str(line_count))

                summary = self.process_syrx_records(records, bad_record_file)
                rv.num_good_records += summary.num_good_records
                rv.num_bad_records += summary.num_bad_records
                rv.record_ranges += summary.record_ranges

                last_processed += 200
                records = []

        return rv

    def process_syrx_records(self, records, bad_record_file):
        # each record has properties date_added, timestamp, value, syrx_num

        equipment_point_records_return = self.get_equipment_point_records(records)

        if len(equipment_point_records_return.equipment_point_records) > 0:
            self.delete_old_records(equipment_point_records_return.equipment_point_records)
            self.insert_records(equipment_point_records_return.equipment_point_records)

        if len(equipment_point_records_return.bad_records) > 0:
            for r in equipment_point_records_return.bad_records:
                bad_record_file.write(json.dumps(r) + u"\n")

        rv = ProcessSyrxRecordsReturn()
        rv.num_good_records = len(equipment_point_records_return.equipment_point_records)
        rv.num_bad_records = len(equipment_point_records_return.bad_records)
        rv.record_ranges = self.get_record_ranges(equipment_point_records_return.equipment_point_records)

        return rv

    def populate_weatherstation_id_on_records(self, records):
        syrx_nums = self.get_unique_syrx_nums(records)
        weatherstation_ids_by_syrx_num = self.uow.component_points.get_weatherstation_ids_for_syrx_numbers(syrx_nums)
        for r in records:
            if r["syrx_num"] not in weatherstation_ids_by_syrx_num:
                continue
            weatherstation_id = weatherstation_ids_by_syrx_num[r["syrx_num"]]
            r["weatherstation_id"] = weatherstation_id

    def get_weather_data(self, records):
        weatherstation_years_to_retrieve = self.get_weatherstation_years_to_retrieve(records)
        weather_data = self.get_weather_data_records(weatherstation_years_to_retrieve)
        return weather_data

    def get_weatherstation_years_to_retrieve(self, records):
        weatherstation_years_to_retrieve = defaultdict(set)
        for r in records:
            try:
                year = pytz.utc.localize(dateutil.parser.parse(r["timestamp"])).year
                weatherstation_years_to_retrieve[r["weatherstation_id"]].add(year)
            except:
                pass

        return weatherstation_years_to_retrieve

    def get_weather_data_records(self, weatherstation_years_to_retrieve):
        weather_data = dict()
        for weatherstation_id, years_set in weatherstation_years_to_retrieve.iteritems():
            years = list(years_set)

            weatherstation_data = self.uow.weather_stations.get_noaa_records(weatherstation_id, years)
            weatherstation_data = dict((d["datetimeutc"], d) for d in weatherstation_data)

            weather_data[weatherstation_id] = weatherstation_data

        return weather_data

    def get_equipment_point_records(self, records):
        rv = EquipmentPointRecordsReturn()

        self.populate_weatherstation_id_on_records(records)
        # weather_data is a dict keyed by the weatherstation id
        try:
            weather_data = self.get_weather_data(records)
        except:
            weather_data = dict()

        for row in records:
            error_messages = []

            row["error"] = {
                "date": self.date_time_str,
                "messages": error_messages
            }

            equipment_point_record = None
            value = None

            try:
                value = float(row["value"])
            except:
                error_messages.append("Value is not a number")

            try:
                date = pytz.utc.localize(dateutil.parser.parse(row["timestamp"]))
                syrx_num = row["syrx_num"]
                weather = None

                weather_time = date.replace(minute=0)

                if "weatherstation_id" not in row or row["weatherstation_id"] not in weather_data:
                    error_messages.append("Weatherstation not found")
                elif weather_time not in weather_data[row["weatherstation_id"]]:
                    weather_time_str = weather_time.strftime("%Y-%m-%d %H:%M:%S")
                    error_messages.append("Time " + weather_time_str + " not found in weather data")
                else:
                    weather = weather_data[row["weatherstation_id"]][weather_time]

                equipment_point_record = self.uow.energy_records.get_equipment_point_record(date, syrx_num,
                                                                                            value, weather,
                                                                                            self.date_time)
            except:
                error_messages.append("Timestamp could not be parsed")

            if len(error_messages) == 0 and equipment_point_record is not None:
                rv.equipment_point_records.append(equipment_point_record)
            else:
                rv.bad_records.append(row)

        return rv

    def delete_old_records(self, equipment_point_records):
        keys = [[r["syrx_num"], r["date"]] for r in equipment_point_records]
        self.uow.energy_records.delete_equipment_point_records(keys)

    def insert_records(self, equipment_point_records):
        self.uow.energy_records.insert_equipment_point_records(equipment_point_records)

    def get_record_ranges(self, equipment_point_records):
        ranges = []

        grouped_by_syrx = [(k, list(v)) for k, v in groupby(equipment_point_records, lambda x: x["syrx_num"])]

        for syrx_num, records in grouped_by_syrx:
            dates = map(lambda x: x["date"], records)

            r = RecordRange()
            r.syrx_num = syrx_num
            r.start_date = min(dates)
            r.end_date = max(dates)

            ranges.append(r)

        return ranges

    def compile_equipment_point_records(self, ranges):
        compiler = EnergyRecordCompiler()
        for r in ranges:
            syrx_num = r.syrx_num
            start_date = r.start_date
            end_date = r.end_date
            self.uow.compiled_energy_records.delete_compiled_equipment_point_records(syrx_num, start_date, end_date)
            compiler.compile_component_point_records_by_year_span(syrx_num, start_date, end_date)

    def flatten_record_ranges(self, record_ranges):
        record_ranges_by_syrx_num = dict()
        for r in record_ranges:
            if r.syrx_num not in record_ranges_by_syrx_num:
                record_ranges_by_syrx_num[r.syrx_num] = r
            else:
                record_ranges_by_syrx_num[r.syrx_num].start_date = min(record_ranges_by_syrx_num[r.syrx_num].start_date, r.start_date)
                record_ranges_by_syrx_num[r.syrx_num].end_date = max(record_ranges_by_syrx_num[r.syrx_num].end_date, r.end_date)

        return record_ranges_by_syrx_num.values()

    def get_unique_syrx_nums(self, records):
        syrx_nums = list(set(map(lambda x: x["syrx_num"], records)))
        return syrx_nums