import base64
from collections import defaultdict
import datetime
import json
from shutil import move
from tempfile import NamedTemporaryFile
import dateutil.parser
from db.uow import UoW
from os import listdir, path, remove
import os
import pytz


class ProcessJohnsonRecordsSummaryReturn:
    def __init__(self):
        self.num_good_records = 0
        self.num_bad_records = 0
        self.num_unmapped_vendor_points = 0
        self.num_global_vendor_point_records = 0


class ProcessJohnsonRecordsReturn:
    def __init__(self):
        self.good_records = []
        self.bad_records = []
        self.unmapped_vendor_points = []
        self.global_vendor_point_records = []


class JohnsonFileHandler():
    def __init__(self):
        self.johnson_grouped_folder = ""
        self.syrx_upload_folder = ""
        self.logger = None
        self.uow = UoW(None)

        self.date_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d")
        self.date_time_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")

        self.mapped_vendor_points = []

    def run(self):
        self.get_mapped_vendor_points()
        self.process_all_johnson_files()

    def get_mapped_vendor_points(self):
        self.mapped_vendor_points = self.uow.data_mapping.get_all_mappings_for_johnson()

    def process_all_johnson_files(self):
        for mapping in self.mapped_vendor_points:
            site_id = mapping["johnson_site_id"]
            fqr = mapping["johnson_fqr"]
            self.logger.debug("Processing vendor data for site_id=" + site_id + ", fqr=" + fqr)
            dest_dir = self.get_destination_directory(site_id, fqr)

            if os.path.exists(dest_dir):
                self.process_johnson_files_in_dir(dest_dir)
            else:
                self.logger.debug("Directory does not exist for site_id=" + site_id + ", fqr=" + fqr)
            self.logger.debug("Finished processing vendor data for site_id=" + site_id + ", fqr=" + fqr)

    def process_johnson_files_in_dir(self, dir):
        file_names = listdir(dir)
        self.logger.debug("Found " + str(len(file_names)) + " johnson file(s) to process")

        file_count = len(file_names)
        for i, file_name in enumerate(file_names):
            self.process_johnson_filename(i, dir, file_name, file_count)

        self.logger.debug("Finished processing johnson files")

    def process_johnson_filename(self, index, containing_directory, file_name, file_count):
        self.logger.debug("Processing file " + str(index + 1) + "/" + str(file_count))
        file_path = path.join(containing_directory, file_name)
        self.logger.debug("File path: " + file_path)

        try:
            self.process_johnson_file_path(file_path)
        except:
            self.logger.exception("An error occurred processing johnson file located at " + file_path)

    def process_johnson_file_path(self, file_path):
        bad_record_file = NamedTemporaryFile(delete=False)
        good_record_file_path = path.join(self.syrx_upload_folder, self.date_str)

        with open(good_record_file_path, "a") as good_record_file:
            with open(file_path, "r") as f:
                summary = self.process_johnson_file(f, good_record_file, bad_record_file)

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

    def process_johnson_file(self, read_file, good_record_file, bad_record_file):
        rv = ProcessJohnsonRecordsSummaryReturn()

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

                summary = self.process_johnson_records(records, good_record_file, bad_record_file)
                rv.num_good_records += summary.num_good_records
                rv.num_bad_records += summary.num_bad_records
                rv.num_global_vendor_point_records += summary.num_global_vendor_point_records
                rv.num_unmapped_vendor_points += summary.num_unmapped_vendor_points

                last_processed += 200
                records = []

        return rv

    def process_johnson_records(self, records, good_record_file, bad_record_file):

        processed_records = self.get_processed_johnson_records(records)

        if len(processed_records.good_records) > 0:
            for r in processed_records.good_records:
                good_record_file.write(json.dumps(r) + u"\n")
        if len(processed_records.bad_records) > 0:
            for r in processed_records.bad_records:
                bad_record_file.write(json.dumps(r) + u"\n")

        if len(processed_records.unmapped_vendor_points) > 0:
            self.handle_unmapped_vendor_points(processed_records.unmapped_vendor_points)

        # make records unique
        processed_records.global_vendor_point_records = self.make_global_vendor_point_records_unique(records[0]['site_id'],
                                                                                                     records[0]['fqr'],
                                                                                                     processed_records.global_vendor_point_records)
        # insert records
        self.uow.global_vendor_point_records.insert_global_vendor_point_records(processed_records.global_vendor_point_records)

        rv = ProcessJohnsonRecordsSummaryReturn()
        rv.num_good_records = len(processed_records.good_records)
        rv.num_bad_records = len(processed_records.bad_records)
        rv.num_unmapped_vendor_points = len(processed_records.unmapped_vendor_points)
        rv.num_global_vendor_point_records = len(processed_records.global_vendor_point_records)

        return rv

    def get_processed_johnson_records(self, records):
        rv = ProcessJohnsonRecordsReturn()
        # fields of record in records object:
        # site_id, fqr, timestamp, value, reliability, date_added

        mappings_dict = self.get_mappings_dict(records)

        for r in records:
            site_id = r["site_id"]
            fqr = r["fqr"]
            reliability = r["reliability"]

            error_messages = []

            r["error"] = {
                "date": self.date_time_str,
                "messages": error_messages
            }

            if reliability.upper() != "RELIABLE":
                error_messages.append("Record unreliable")

            if (site_id, fqr) not in mappings_dict:
                error_messages.append("Could not find vendor mapping")
                rv.unmapped_vendor_points.append({
                    "source": "johnson",
                    "johnson_site_id": site_id,
                    "johnson_fqr": fqr,
                    "date_added": self.date_time_str
                })
            else:
                mappings = mappings_dict[site_id, fqr]
                # check to see if the mapping is global and handle accordingly
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
        # update the mapping to only have information that is necessary for global vendor points
        proper_mapping = {
            'source': 'johnson',
            'johnson_site_id': str(row["site_id"]),
            'johnson_fqr': str(row["fqr"])
        }
        if mapping["point_type"] in ["EP", "NP", "PP"]:
            try:
                row["value"] = float(row["value"])
            except ValueError:
                error_messages.append("Invalid value for energy/numeric/position point")
                proper_mapping = None

        elif mapping["point_type"] == "BP":
            if row["value"].upper() == "ON" or row["value"].upper() == "RUN":
                row["value"] = 1.0
            elif row["value"].upper() == "OFF" or row["value"].upper() == "STOP":
                row["value"] = 0.0
            else:
                error_messages.append("Invalid value for boolean point")
                proper_mapping = None
        else:
            error_messages.append("Invalid point type")
            proper_mapping = None

        if len(error_messages) == 0:

            try:
                date = pytz.utc.localize(dateutil.parser.parse(row["timestamp"]))
                proper_mapping["timestamp"] = self.get_string_timestamp(row["timestamp"])
                proper_mapping["date"] = date
                proper_mapping["value"] = row["value"]
                proper_mapping["date_added"] = self.date_time_str
            except:
                error_messages.append("Could not parse timestamp")
                proper_mapping = None
        return proper_mapping

    def get_mappings_dict(self, records):
        keys = [[r["site_id"], r["fqr"]] for r in records]
        mappings = self.uow.data_mapping.get_mappings_for_johnson_site_id_fqr(keys)
        mappings_dict = defaultdict(list)
        for r in mappings:
            mappings_dict[(r['johnson_site_id'], r['johnson_fqr'])].append(r)

        return mappings_dict

    @staticmethod
    def get_string_timestamp(timestamp):
        return pytz.utc.localize(dateutil.parser.parse(timestamp)).strftime("%Y-%m-%d %H:%M:%S")

    def handle_unmapped_vendor_points(self, unmapped_vendor_points):
        keys = list(set([(r["johnson_site_id"], r["johnson_fqr"]) for r in unmapped_vendor_points]))
        detupled_keys = [list(r) for r in keys]
        db_unmapped_vendor_points = self.uow.data_mapping.get_unknown_vendor_points_for_johnson_site_id_fqr(detupled_keys)
        db_unmapped_vendor_points = dict(((r["johnson_site_id"], r["johnson_fqr"]), r) for r in db_unmapped_vendor_points)

        filtered_unmapped_vendor_points = [{"johnson_site_id": r[0], "johnson_fqr": r[1],
                                            "source": "johnson", "date_added": self.date_str} for r in keys
                                           if r not in db_unmapped_vendor_points]
        self.uow.data_mapping.insert_unknown_vendor_points(filtered_unmapped_vendor_points)

    def get_destination_directory(self, site_id, fqr):
        site_id = base64.urlsafe_b64encode(site_id)
        fqr = base64.urlsafe_b64encode(fqr)
        dest_dir = os.path.join(self.johnson_grouped_folder, site_id, fqr)
        return dest_dir

    def make_global_vendor_point_records_unique(self, site_id, fqr, global_vendor_point_records):
        # ensure unique before inserting
        existing_dates = self.uow.global_vendor_point_records.get_existing_dates_for_johnson(site_id, fqr)
        records_by_date = defaultdict(dict)
        for r in global_vendor_point_records:
            records_by_date[r['date']] = r

        # gets the intersection of the existing dates and the global vendor point records
        # dates returned will be removed to prevent duplicate data in the DB
        dates_to_remove = list(set(existing_dates).intersection(set(records_by_date.keys())))
        for d in dates_to_remove:
            del records_by_date[d]

        return records_by_date.values()