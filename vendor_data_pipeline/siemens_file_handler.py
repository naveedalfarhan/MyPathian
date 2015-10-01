import base64
from collections import defaultdict
import datetime
import json
from shutil import move
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree
import dateutil.parser
from db.uow import UoW
from os import listdir, path, remove
import os
import pytz

__author__ = 'badams'


class ProcessSiemensRecordsSummaryReturn:
    def __init__(self):
        self.num_good_records = 0
        self.num_bad_records = 0
        self.num_unmapped_vendor_points = 0
        self.num_global_vendor_point_records = 0


class ProcessSiemensRecordsReturn:
    def __init__(self):
        self.good_records = []
        self.bad_records = []
        self.unmapped_vendor_points = []
        self.global_vendor_point_records = []


class SiemensFileHandler():
    def __init__(self):
        self.siemens_grouped_folder = ""
        self.syrx_upload_folder = ""
        self.logger = None
        self.uow = UoW(None)

        self.date_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d")
        self.date_time_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")

        self.mapped_vendor_points = []

    def run(self):
        self.get_mapped_vendor_points()
        self.process_all_siemens_files()

    def get_mapped_vendor_points(self):
        self.mapped_vendor_points = self.uow.data_mapping.get_all_mappings_for_siemens()

    def process_all_siemens_files(self):
        for mapping in self.mapped_vendor_points:
            meter_name = mapping["siemens_meter_name"]
            self.logger.debug("Processing vendor data for meter_name=" + meter_name)
            dest_dir = self.get_destination_directory(meter_name)

            if os.path.exists(dest_dir):
                self.process_siemens_files_in_dir(dest_dir)
            else:
                self.logger.debug("Directory does not exist for meter_name=" + meter_name)
            self.logger.debug("Finished processing vendor data for meter_name=" + meter_name)

    def process_siemens_files_in_dir(self, dir):
        file_names = listdir(dir)
        self.logger.debug("Found " + str(len(file_names)) + " siemens file(s) to process")

        file_count = len(file_names)
        for i, file_name in enumerate(file_names):
            self.process_siemens_filename(i, dir, file_name, file_count)

        self.logger.debug("Finished processing siemens files")

    def process_siemens_filename(self, index, containing_directory, file_name, file_count):
        self.logger.debug("Processing file " + str(index + 1) + "/" + str(file_count))
        file_path = path.join(containing_directory, file_name)
        self.logger.debug("File path: " + file_path)

        try:
            self.process_siemens_file_path(file_path)
        except:
            self.logger.exception("An error occurred processing siemens file located at " + file_path)
            
    def process_siemens_file_path(self, file_path):
        bad_record_file = NamedTemporaryFile(delete=False)
        good_record_file_path = path.join(self.syrx_upload_folder, self.date_str)

        with open(good_record_file_path, "a") as good_record_file:
            with open(file_path, "r") as f:
                summary = self.process_siemens_file(f, good_record_file, bad_record_file)

        remove(file_path)

        bad_record_file.close()
        if summary.num_bad_records == 0:
            remove(bad_record_file.name)
        else:
            move(bad_record_file.name, file_path)

        self.logger.debug("Found " + str(summary.num_good_records) + " good record(s)")
        self.logger.debug("Found " + str(summary.num_bad_records) + " bad record(s)")
        self.logger.debug("Found " + str(summary.num_global_vendor_point_records) + " global vendor point record(s)")
        self.logger.debug("Inserted " + str(summary.num_unmapped_vendor_points) + " unmapped vendor point(s)")
        
    def process_siemens_file(self, read_file, good_record_file, bad_record_file):
        rv = ProcessSiemensRecordsSummaryReturn()

        records = []

        line_count = 0
        for line in read_file:
            line_count += 1

        read_file.seek(0)

        self.logger.debug("Found " + str(line_count) + " lines")

        line_no = 0
        last_processed = 0
        for line in read_file:
            records.append(json.loads(line))
            line_no += 1

            if len(records) % 200 == 0 or line_no == line_count:
                self.logger.debug("Processing lines " + str(last_processed + 1) + "-" +
                                  str(last_processed + 200) + " of " + str(line_count))

                summary = self.process_siemens_records(records, good_record_file, bad_record_file)
                rv.num_good_records += summary.num_good_records
                rv.num_bad_records += summary.num_bad_records
                rv.num_global_vendor_point_records += summary.num_global_vendor_point_records
                rv.num_unmapped_vendor_points += summary.num_unmapped_vendor_points

                last_processed += 200
                records = []

        return rv

    def process_siemens_records(self, records, good_record_file, bad_record_file):

        processed_records = self.get_processed_siemens_records(records)

        if len(processed_records.good_records) > 0:
            for r in processed_records.good_records:
                good_record_file.write(json.dumps(r) + u"\n")
        if len(processed_records.bad_records) > 0:
            for r in processed_records.bad_records:
                bad_record_file.write(json.dumps(r) + u"\n")

        if len(processed_records.unmapped_vendor_points) > 0:
            self.handle_unmapped_vendor_points(processed_records.unmapped_vendor_points)

        # make records unique
        processed_records.global_vendor_point_records = self.make_global_vendor_point_records_unique(records[0]['siemens_meter_name'],
                                                                                                     processed_records.global_vendor_point_records)

        # insert global vendor_vendor_point_records
        self.uow.global_vendor_point_records.insert_global_vendor_point_records(processed_records.global_vendor_point_records)

        rv = ProcessSiemensRecordsSummaryReturn()
        rv.num_good_records = len(processed_records.good_records)
        rv.num_bad_records = len(processed_records.bad_records)
        rv.num_unmapped_vendor_points = len(processed_records.unmapped_vendor_points)
        rv.num_global_vendor_point_records = len(processed_records.global_vendor_point_records)

        return rv

    def get_processed_siemens_records(self, records):
        rv = ProcessSiemensRecordsReturn()
        # fields of record in records object:
        # siemens_meter_name, source, date_added, timestamp

        mappings_dict = self.get_mappings_dict(records)

        for r in records:
            meter_name = r["siemens_meter_name"]

            error_messages = []

            r["error"] = {
                "date": self.date_time_str,
                "messages": error_messages
            }

            if meter_name not in mappings_dict:
                error_messages.append("Could not find vendor mapping")
                rv.unmapped_vendor_points.append({
                    "source": "siemens",
                    "siemens_meter_name": meter_name,
                    "date_added": self.date_time_str
                })
            else:
                mappings = mappings_dict[meter_name]
                if 'global' in mappings[0] and mappings[0]['global']:
                    self._handle_global_mapping(mappings[0], r, rv, error_messages)
                else:
                    self._handle_record(mappings[0], r, rv, error_messages)

                if len(error_messages) < 1:
                    continue

            rv.bad_records.append(r)

        return rv

    def _handle_global_mapping(self, mapping, row, rv, error_messages):
        # get a global record that can be inserted into the database
        good_record = self._get_global_vendor_point_record(mapping, row, error_messages)
        if len(error_messages) < 1:
            rv.global_vendor_point_records.append(good_record)

    def _handle_record(self, mapping, row, rv, error_messages):
        if mapping["point_type"] in ["EP", "NP", "PP"]:
            try:
                row["value"] = float(row["value"])
            except ValueError:
                error_messages.append("Invalid value for energy/numeric/position point")

        elif mapping["point_type"] == "BP":
            if row["value"].upper() == "ON" or row["value"].upper() == "RUN":
                row["value"] = 1.0
            elif row["value"].upper() == "OFF" or row["value"].upper() == "STOP":
                row["value"] = 0.0
            else:
                error_messages.append("Invalid value for boolean point")
        else:
            error_messages.append("Invalid point type")

        if len(error_messages) == 0:

            try:
                row["timestamp"] = self.get_string_timestamp(row["timestamp"])
                good_record = {
                    "syrx_num": mapping["syrx_num"],
                    "timestamp": row["timestamp"],
                    "value": row["value"],
                    "date_added": self.date_time_str
                }
                rv.good_records.append(good_record)
            except:
                error_messages.append("Could not parse timestamp")

    def _get_global_vendor_point_record(self, mapping, row, error_messages):
        # get a global record that can be inserted into the database
        global_record = {
            "source": "siemens",
            "siemens_meter_name": row["siemens_meter_name"]
        }

        if mapping["point_type"] in ["EP", "NP", "PP"]:
            try:
                row["value"] = float(row["value"])
            except ValueError:
                error_messages.append("Invalid value for energy/numeric/position point")
                global_record = None

        elif mapping["point_type"] == "BP":
            if row["value"].upper() == "ON" or row["value"].upper() == "RUN":
                row["value"] = 1.0
            elif row["value"].upper() == "OFF" or row["value"].upper() == "STOP":
                row["value"] = 0.0
            else:
                error_messages.append("Invalid value for boolean point")
                global_record = None
        else:
            error_messages.append("Invalid point type")
            global_record = None

        if len(error_messages) == 0:

            try:
                date = pytz.utc.localize(dateutil.parser.parse(row["timestamp"]))
                row["timestamp"] = self.get_string_timestamp(row["timestamp"])
                global_record["timestamp"] = row["timestamp"]
                global_record["date"] = date
                global_record["value"] = row["value"]
                global_record["date_added"] = self.date_time_str
            except:
                error_messages.append("Could not parse timestamp")
                global_record = None

        return global_record

    def get_mappings_dict(self, records):
        keys = [[r["siemens_meter_name"]] for r in records]
        mappings = self.uow.data_mapping.get_mappings_for_siemens_meter_name(keys)
        mappings_dict = defaultdict(list)
        for r in mappings:
            mappings_dict[r["siemens_meter_name"]].append(r)

        return mappings_dict

    @staticmethod
    def get_string_timestamp(timestamp):
        return pytz.utc.localize(dateutil.parser.parse(timestamp)).strftime("%Y-%m-%d %H:%M:%S")

    def handle_unmapped_vendor_points(self, unmapped_vendor_points):
        # leaving the comma while forming the tuple tells python that we are trying to create a one element tuple,
        # so it then gets detupled properly
        keys = list(set([(r["siemens_meter_name"],) for r in unmapped_vendor_points]))
        detupled_keys = [list(r) for r in keys]
        db_unmapped_vendor_points = self.uow.data_mapping.get_unknown_vendor_points_for_siemens_meter_name(detupled_keys)
        db_unmapped_vendor_points = dict(((r["siemens_meter_name"],), r) for r in db_unmapped_vendor_points)

        filtered_unmapped_vendor_points = [{"siemens_meter_name": r[0], "source": "siemens",
                                            "date_added": self.date_str} for r in keys
                                           if r not in db_unmapped_vendor_points]
        self.uow.data_mapping.insert_unknown_vendor_points(filtered_unmapped_vendor_points)

    def get_destination_directory(self, meter_name):
        meter_name = base64.urlsafe_b64encode(meter_name)
        dest_dir = os.path.join(self.siemens_grouped_folder, meter_name)
        return dest_dir

    def make_global_vendor_point_records_unique(self, meter_name, global_vendor_point_records):
        # ensure unique before inserting
        existing_dates = self.uow.global_vendor_point_records.get_existing_dates_for_siemens(meter_name)
        records_by_date = defaultdict(dict)
        for r in global_vendor_point_records:
            records_by_date[r['date']] = r

        # gets the intersection of the existing dates and the global vendor point records
        # dates returned will be removed to prevent duplicate data in the DB
        dates_to_remove = list(set(existing_dates).intersection(set(records_by_date.keys())))
        for d in dates_to_remove:
            del records_by_date[d]

        return records_by_date.values()