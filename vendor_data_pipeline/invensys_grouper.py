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

class ProcessInvensysRecordsSummaryReturn:
    def __init__(self):
        self.num_good_records = 0
        self.num_bad_records = 0
        self.num_unmapped_vendor_points = 0

class ProcessInvensysRecordsReturn:
    def __init__(self):
        self.good_records = []
        self.bad_records = []
        self.unmapped_vendor_points = []

class InvensysGrouper():
    def __init__(self):
        self.invensys_raw_folder = ""
        self.invensys_grouped_folder = ""
        self.logger = None
        self.uow = UoW(None)

        self.date_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d")
        self.date_time_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")

    def process_all_invensys_files(self):
        file_names = listdir(self.invensys_raw_folder)
        self.logger.debug("Found " + str(len(file_names)) + " invensys file(s) to process")

        file_count = len(file_names)
        for i, file_name in enumerate(file_names):
            self.process_invensys_filename(i, file_name, file_count)

        self.logger.debug("Finished processing invensys files")

    def process_invensys_filename(self, index, file_name, file_count):
        self.logger.debug("Processing file " + str(index + 1) + "/" + str(file_count))
        file_path = os.path.join(self.invensys_raw_folder, file_name)
        self.logger.debug("File path: " + file_path)

        if file_name == self.date_str:
            self.logger.debug("Ignoring today's file")
            return

        try:
            self.process_invensys_file_path(file_path)
        except:
            self.logger.exception("An error occurred processing invensys file located at " + file_path)


    def process_invensys_file_path(self, file_path):
        bad_record_file = NamedTemporaryFile(delete=False)

        with open(file_path, "r") as f:
            summary = self.process_invensys_file(f, bad_record_file)

        remove(file_path)
        bad_record_file.close()
        if summary.num_bad_records == 0:
            remove(bad_record_file.name)
        else:
            move(bad_record_file.name, file_path)

    def process_invensys_file(self, read_file, bad_record_file):
        rv = ProcessInvensysRecordsSummaryReturn()

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
                site_name = r["invensys_site_name"]
                equipment_name = r["invensys_equipment_name"]
                point_name = r["invensys_point_name"]

                try:
                    grouped_records[(site_name, equipment_name, point_name)].append(r)
                except KeyError:
                    grouped_records[(site_name, equipment_name, point_name)] = [r]

                num_records += 1
                rv.num_good_records += 1
            except KeyError:
                bad_record_file.write(json.dumps(r) + u"\n")
                rv.num_bad_records += 1



            if num_records % 200 == 0 or line_no == line_count:
                self.logger.debug("Processing lines " + str(last_processed + 1) + "-" +
                                  str(last_processed + 200) + " of " + str(line_count))

                process_return = self.process_invensys_records(grouped_records)
                if len(process_return.unmapped_vendor_points) > 0:
                    self.handle_unmapped_vendor_points(process_return.unmapped_vendor_points)

                last_processed += 200
                num_records = 0
                grouped_records = dict()

        return rv

    def process_invensys_records(self, grouped_records):
        rv = ProcessInvensysRecordsReturn()
        mappings_dict = self.get_mappings_dict(grouped_records.keys())

        for k, v in grouped_records.iteritems():
            site_name = k[0]
            equipment_name = k[1]
            point_name = k[2]


            if (site_name, equipment_name, point_name) not in mappings_dict:
                rv.unmapped_vendor_points.append({
                    "source": "invensys",
                    "invensys_site_name": site_name,
                    "invensys_equipment_name": equipment_name,
                    "invensys_point_name": point_name,
                    "date_added": self.date_time_str
                })

            dest_dir = self.get_destination_directory(site_name, equipment_name, point_name)

            try:
                makedirs(dest_dir)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

            good_record_file_path = os.path.join(dest_dir, self.date_str)
            with open(good_record_file_path, "a") as f:
                for r in v:
                    f.write(json.dumps(r) + u"\n")

        return rv

    def get_mappings_dict(self, records):
        keys = [[r[0], r[1], r[2]] for r in records]
        mappings = self.uow.data_mapping.get_mappings_for_invensys_site_equipment_point(keys)
        mappings_dict = dict(((r["invensys_site_name"], r["invensys_equipment_name"], r["invensys_point_name"]), r) for r in mappings)

        return mappings_dict

    def handle_unmapped_vendor_points(self, unmapped_vendor_points):
        db_unmapped_vendor_points = self.uow.data_mapping.get_unknown_vendor_points_for_invensys()
        db_unmapped_vendor_points = dict(((r["invensys_site_name"], r["invensys_equipment_name"], r["invensys_point_name"]), r) for r in db_unmapped_vendor_points)

        filtered_unmapped_vendor_points = [r for r in unmapped_vendor_points
                                           if (r["invensys_site_name"], r["invensys_equipment_name"], r["invensys_point_name"]) not in db_unmapped_vendor_points]
        self.uow.data_mapping.insert_unknown_vendor_points(filtered_unmapped_vendor_points)

    def get_destination_directory(self, site_name, equipment_name, point_name):
        site_name = base64.urlsafe_b64encode(site_name)
        equipment_name = base64.urlsafe_b64encode(equipment_name)
        point_name = base64.urlsafe_b64encode(point_name)
        dest_dir = os.path.join(self.invensys_grouped_folder, site_name, equipment_name, point_name)
        return dest_dir
