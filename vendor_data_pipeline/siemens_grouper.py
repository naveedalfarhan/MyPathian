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
from xml.etree import ElementTree

class ProcessSiemensRecordsSummaryReturn:
    def __init__(self):
        self.num_good_records = 0
        self.num_bad_records = 0
        self.num_unmapped_vendor_points = 0

class ProcessSiemensRecordsReturn:
    def __init__(self):
        self.good_records = []
        self.bad_records = []
        self.unmapped_vendor_points = []

class SiemensGrouper():
    def __init__(self):
        self.siemens_xml_folder = ""
        self.siemens_raw_folder = ""
        self.siemens_grouped_folder = ""
        self.logger = None
        self.uow = UoW(None)

        self.date_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d")
        self.date_time_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")

    def run(self):
        self.convert_all_files_to_json()
        self.process_all_siemens_files()

    def convert_all_files_to_json(self):
        xml_file_names = listdir(self.siemens_xml_folder)
        self.logger.debug("Found" + str(len(xml_file_names)) + " siemens xml file(s) to convert to json")

        xml_file_count = len(xml_file_names)
        for i, file_name in enumerate(xml_file_names):
            self.process_xml_file(i, file_name, xml_file_count)

        self.logger.debug("Finished converting xml files to json")

    def process_xml_file(self, index, file_name, file_count):
        self.logger.debug("Converting file" + str(index + 1) + "/" + str(file_count))
        file_path = os.path.join(self.siemens_xml_folder, file_name)

        # compare the file name vs the current date string and ignore if the file is today's file
        # file_name in from YYYYMMDD-hhmmss_SiemensBNH@Input_.xml and date_str in YYYY-MM-DD
        if file_name[:8] == self.date_str.replace('-', ''):
            self.logger.debug("Ignoring today's file")
            return

        try:
            self.process_xml_file_path(file_path)
        except:
            self.logger.exception("An error occured converting siemens xml file to json located at "  + file_path)

    def process_xml_file_path(self, file_path):
        json_record_file_path = os.path.join(self.siemens_raw_folder, self.date_str)

        with open(json_record_file_path, "a") as json_record_file:
            with open(file_path, "r") as f:
                success = self.convert_xml_file_to_json(f, json_record_file)

        if success:
            remove(file_path)
            self.logger.debug("XML file at " + file_path + " successfully converted to json in " + json_record_file_path)
        else:
            self.logger.debug("XML file at " + file_path + " could not be converted to json.")

    def convert_xml_file_to_json(self, xml_file, json_file):
        try:
            tree = ElementTree.parse(xml_file)
            root = tree.getroot()
        except:
            self.logger.debug("Failed to parse XML file.")
            return False

        records_to_write = []

        if root.tag == "Meters":
            for child in root:
                if child.tag == "Meter":
                    json_doc = {}
                    child_attrs = child.attrib
                    if "name" not in child_attrs or "timestamp" not in child_attrs:
                        self.logger.debug("XML file not in the proper format.")
                        return False
                    json_doc['siemens_meter_name'] = child_attrs["name"]
                    json_doc["timestamp"] = child_attrs["timestamp"]
                    # make sure the child has children
                    if len(child):
                        json_doc["value"] = child[0].text
                    else:
                        json_doc["value"] = "0"

                    records_to_write.append(json_doc)
                else:
                    self.logger.debug("XML file not in the proper format")
                    return False

        # write json document to the file
        for row in records_to_write:
            json_file.write(json.dumps(row) + u"\n")
        return True

    def process_all_siemens_files(self):
        file_names = listdir(self.siemens_raw_folder)
        self.logger.debug("Found " + str(len(file_names)) + " siemens file(s) to process")

        file_count = len(file_names)
        for i, file_name in enumerate(file_names):
            self.process_siemens_filename(i, file_name, file_count)

        self.logger.debug("Finished processing siemens files")

    def process_siemens_filename(self, index, file_name, file_count):
        self.logger.debug("Processing file " + str(index + 1) + "/" + str(file_count))
        file_path = os.path.join(self.siemens_raw_folder, file_name)
        self.logger.debug("File path: " + file_path)

        try:
            self.process_siemens_file_path(file_path)
        except:
            self.logger.exception("An error occurred processing siemens file located at " + file_path)


    def process_siemens_file_path(self, file_path):
        bad_record_file = NamedTemporaryFile(delete=False)

        with open(file_path, "r") as f:
            summary = self.process_siemens_file(f, bad_record_file)

        remove(file_path)
        bad_record_file.close()
        if summary.num_bad_records == 0:
            remove(bad_record_file.name)
        else:
            move(bad_record_file.name, file_path)

    def process_siemens_file(self, read_file, bad_record_file):
        rv = ProcessSiemensRecordsSummaryReturn()

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
            line_no += 1

            try:
                r = json.loads(line)
                try:
                    meter_name = r["siemens_meter_name"]

                    try:
                        grouped_records[meter_name].append(r)
                    except KeyError:
                        grouped_records[meter_name] = [r]

                    num_records += 1
                    rv.num_good_records += 1
                except KeyError:
                    bad_record_file.write(json.dumps(r) + u"\n")
                    rv.num_bad_records += 1

            except:
                # not a json record, ignore
                pass



            if num_records % 200 == 0:
                self.logger.debug("Processing lines " + str(last_processed + 1) + "-" +
                                  str(last_processed + 200) + " of " + str(line_count))

                process_return = self.process_siemens_records(grouped_records)
                if len(process_return.unmapped_vendor_points) > 0:
                    self.handle_unmapped_vendor_points(process_return.unmapped_vendor_points)

                last_processed += 200
                num_records = 0
                grouped_records = dict()


        if num_records > 0:
            self.logger.debug("Processing lines " + str(last_processed + 1) + "-" +
                              str(last_processed + 200) + " of " + str(line_count))

            process_return = self.process_siemens_records(grouped_records)
            if len(process_return.unmapped_vendor_points) > 0:
                self.handle_unmapped_vendor_points(process_return.unmapped_vendor_points)
        return rv

    def process_siemens_records(self, grouped_records):
        rv = ProcessSiemensRecordsReturn()
        mappings_dict = self.get_mappings_dict(grouped_records.keys())

        for meter_name, v in grouped_records.iteritems():
            if meter_name not in mappings_dict:
                rv.unmapped_vendor_points.append({
                    "source": "siemens",
                    "siemens_meter_name": meter_name,
                    "date_added": self.date_time_str
                })

            dest_dir = self.get_destination_directory(meter_name)

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
        keys = [r for r in records]
        mappings = self.uow.data_mapping.get_mappings_for_siemens_meter_name(keys)
        mappings_dict = dict((r["siemens_meter_name"], r) for r in mappings)

        return mappings_dict

    def handle_unmapped_vendor_points(self, unmapped_vendor_points):
        db_unmapped_vendor_points = self.uow.data_mapping.get_unknown_vendor_points_for_siemens()
        db_unmapped_vendor_points = dict((r["siemens_meter_name"], r) for r in db_unmapped_vendor_points)

        filtered_unmapped_vendor_points = [r for r in unmapped_vendor_points
                                           if r["siemens_meter_name"] not in db_unmapped_vendor_points]
        self.uow.data_mapping.insert_unknown_vendor_points(filtered_unmapped_vendor_points)

    def get_destination_directory(self, meter_name):
        meter_name = base64.urlsafe_b64encode(meter_name)
        dest_dir = os.path.join(self.siemens_grouped_folder, meter_name)
        return dest_dir