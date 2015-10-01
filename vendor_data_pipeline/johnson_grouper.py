import base64
import datetime
import json
from shutil import move
from sys import path
from tempfile import NamedTemporaryFile
import errno
from os import listdir, remove, makedirs
from db.uow import UoW
import os
import pytz

class ProcessJohnsonRecordsSummaryReturn:
    def __init__(self):
        self.num_good_records = 0
        self.num_bad_records = 0
        self.num_unmapped_vendor_points = 0

class ProcessJohnsonRecordsReturn:
    def __init__(self):
        self.good_records = []
        self.bad_records = []
        self.unmapped_vendor_points = []

class JohnsonGrouper():
    def __init__(self):
        self.johnson_raw_folder = ""
        self.johnson_grouped_folder = ""
        self.logger = None
        self.uow = UoW(None)

        self.date_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d")
        self.date_time_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")

    def process_all_johnson_files(self):
        file_names = listdir(self.johnson_raw_folder)
        self.logger.debug("Found " + str(len(file_names)) + " johnson file(s) to process")

        file_count = len(file_names)
        for i, file_name in enumerate(file_names):
            self.process_johnson_filename(i, file_name, file_count)

        self.logger.debug("Finished processing johnson files")

    def process_johnson_filename(self, index, file_name, file_count):
        self.logger.debug("Processing file " + str(index + 1) + "/" + str(file_count))
        file_path = os.path.join(self.johnson_raw_folder, file_name)
        self.logger.debug("File path: " + file_path)

        if file_name == self.date_str:
            self.logger.debug("Ignoring today's file")
            return

        try:
            self.process_johnson_file_path(file_path)
        except:
            self.logger.exception("An error occurred processing johnson file located at " + file_path)


    def process_johnson_file_path(self, file_path):
        bad_record_file = NamedTemporaryFile(delete=False)

        with open(file_path, "r") as f:
            summary = self.process_johnson_file(f, bad_record_file)

        remove(file_path)
        bad_record_file.close()
        if summary.num_bad_records == 0:
            remove(bad_record_file.name)
        else:
            move(bad_record_file.name, file_path)

    def process_johnson_file(self, read_file, bad_record_file):
        rv = ProcessJohnsonRecordsSummaryReturn()

        num_records = 0
        grouped_records = dict()

        line_count = 0
        for _ in read_file:
            line_count += 1

        read_file.seek(0)

        self.logger.debug("Found " + str(line_count) + " lines")

        line_no = 0
        last_processed = 0
        for line in read_file:
            r = json.loads(line)
            line_no += 1

            try:
                site_id = r["site_id"]
                fqr = r["fqr"]
                try:
                    grouped_records[(site_id, fqr)].append(r)
                except KeyError:
                    grouped_records[(site_id, fqr)] = [r]

                num_records += 1
                rv.num_good_records += 1
            except KeyError:
                bad_record_file.write(json.dumps(r) + u"\n")
                rv.num_bad_records += 1



            if num_records % 1000 == 0:
                self.logger.debug("Processing lines " + str(last_processed + 1) + "-" +
                                  str(last_processed + 1000) + " of " + str(line_count))

                process_return = self.process_johnson_records(grouped_records)
                if len(process_return.unmapped_vendor_points) > 0:
                    self.handle_unmapped_vendor_points(process_return.unmapped_vendor_points)

                last_processed += 1000
                num_records = 0
                grouped_records = dict()

        if num_records > 0:
            self.logger.debug("Processing lines " + str(last_processed + 1) + "-" +
                              str(last_processed + num_records) + " of " + str(line_count))

            process_return = self.process_johnson_records(grouped_records)
            if len(process_return.unmapped_vendor_points) > 0:
                self.handle_unmapped_vendor_points(process_return.unmapped_vendor_points)

        return rv

    def process_johnson_records(self, grouped_records):
        rv = ProcessJohnsonRecordsReturn()
        mappings_dict = self.get_mappings_dict(grouped_records.keys())

        for k, v in grouped_records.iteritems():
            site_id = k[0]
            fqr = k[1]


            if (site_id, fqr) not in mappings_dict:
                rv.unmapped_vendor_points.append({
                    "source": "johnson",
                    "johnson_site_id": site_id,
                    "johnson_fqr": fqr,
                    "date_added": self.date_time_str
                })

            dest_dir = self.get_destination_directory(site_id, fqr)

            if not os.path.exists(dest_dir):
                makedirs(dest_dir)

            good_record_file_path = os.path.join(dest_dir, self.date_str)
            with open(good_record_file_path, "a") as f:
                for r in v:
                    f.write(json.dumps(r) + u"\n")

        return rv

    def get_mappings_dict(self, records):
        keys = [[r[0], r[1]] for r in records]
        mappings = self.uow.data_mapping.get_mappings_for_johnson_site_id_fqr(keys)
        mappings_dict = dict(((r["johnson_site_id"], r["johnson_fqr"]), r) for r in mappings)

        return mappings_dict

    def handle_unmapped_vendor_points(self, unmapped_vendor_points):
        db_unmapped_vendor_points = self.uow.data_mapping.get_unknown_vendor_points_for_johnson()
        db_unmapped_vendor_points = dict(((r["johnson_site_id"], r["johnson_fqr"]), r) for r in db_unmapped_vendor_points)

        filtered_unmapped_vendor_points = [r for r in unmapped_vendor_points
                                           if (r["johnson_site_id"], r["johnson_fqr"]) not in db_unmapped_vendor_points]
        self.uow.data_mapping.insert_unknown_vendor_points(filtered_unmapped_vendor_points)

    def get_destination_directory(self, site_id, fqr):
        site_id = base64.urlsafe_b64encode(site_id)
        fqr = base64.urlsafe_b64encode(fqr)
        dest_dir = os.path.join(self.johnson_grouped_folder, site_id, fqr)
        return dest_dir