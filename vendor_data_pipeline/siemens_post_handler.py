__author__ = 'gopikrishnan'
import base64
import datetime
import json
from shutil import move
from sys import path
import errno
from os import listdir, remove, makedirs
from db.uow import UoW
import os
import pytz
from xml.etree import ElementTree
import datetime

class SiemensGrouper():
    def __init__(self):
        self.siemens_xml_folder = ""
        self.siemens_raw_folder = ""
        self.siemens_grouped_folder = ""
        self.logger = None
        self.uow = UoW(None)
        self.ws_id = None
        self.date_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d")
        self.date_time_str = pytz.utc.localize(datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")
        self.run_timestamp = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    def run(self,added_files):
        self.append_all_files_to_db(added_files)


    def append_all_files_to_db(self, new_files):
        xml_file_names = new_files
        self.logger.debug("Found" + str(len(xml_file_names)) + " siemens xml file(s) to be appended to the database.")

        xml_file_count = len(xml_file_names)
        for file_name in xml_file_names:
            self.process_xml_file(file_name, xml_file_count)

        self.logger.debug("Finished writing xml files to the database.")

    def process_xml_file(self, file_name, file_count):
        #self.logger.debug("Converting file" + str(index + 1) + "/" + str(file_count))
        file_path = os.path.join(self.siemens_xml_folder, file_name)


        # compare the file name vs the current date string and ignore if the file is today's file
        # file_name in from YYYYMMDD-hhmmss_SiemensBNH@Input_.xml and date_str in YYYY-MM-DD
        if file_name[:8] == self.date_str.replace('-', ''):
            self.logger.debug("Ignoring today's file")
            return

        try:
            self.process_xml_file_path(file_path)
        except:
            self.logger.exception("An error occured converting siemens xml file to db located at "  + file_path)

    def process_xml_file_path(self, file_path):
        with open(file_path, "r") as f:
            success = self.convert_xml_file_to_database(f)

        if success:
            remove(file_path)
            self.logger.debug("XML file at " + file_path + " successfully appended to the database.")
        else:
            self.logger.debug("XML file at " + file_path + " could not be appended to the database.")

    def convert_xml_file_to_database(self, xml_file):
        try:
            tree = ElementTree.parse(xml_file)
            root = tree.getroot()
        except:
            self.logger.debug("Failed to parse XML file.")
            return False

        data = []
        if root.tag == "Meters":
            for child in root:
                if child.tag == "Meter":
                    child_attrs = child.attrib
                    if "name" not in child_attrs or "timestamp" not in child_attrs:
                        #self.logger.debug("XML file not in the proper format.")
                        return False
                    sensor_id = child_attrs["name"]

                    # until we know otherwise, assume that siemens timestamps are in eastern standard time
                    local_timestamp = datetime.datetime.strptime(child_attrs["timestamp"], '%m/%d/%Y %H:%M:%S %p')\
                        .replace(tzinfo=pytz.timezone("US/Eastern"))
                    utc_timestamp = local_timestamp.astimezone(pytz.UTC)

                    # make sure the child has children
                    if len(child):
                        value = child[0].text
                    else:
                        value = "0"

                    data.append({
                        "vendor": "siemens",
                        "sensor_id": sensor_id,
                        "siemens_meter_name": child_attrs["name"],
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

            self.uow.vendor_records.insert_vendor_records(data)
            return True
        else:
            self.logger.debug("XML file not in the proper format")
            return False




