from collections import defaultdict
import datetime
import json
from compile_energy_records import EnergyRecordCompiler
from os import path
import dateutil.parser
from db.uow import UoW
import pytz

__author__ = 'badams'


"""
A dictionary difference calculator
Originally posted as:
http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary/1165552#1165552
Found on Github @ https://github.com/hughdbrown/dictdiffer
"""


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])


class GlobalVendorPointHandler:
    def __init__(self):
        self.uow = UoW(None)
        self.logger = None
        self.error_folder = None

        self.date_time = pytz.utc.localize(datetime.datetime.utcnow())
        self.date_time_str = self.date_time.strftime("%Y-%m-%d %H:%M:%S")

    def process_all_global_vendor_points(self):
        gvps = self.uow.data_mapping.get_all_global_vendor_points()
        self.logger.debug("Found " + str(len(gvps)) + " Global Vendor Points.")
        for gvp in gvps:
            self._process_global_vendor_point(gvp)

    def _process_global_vendor_point(self, gvp):
        # determine which index to use based on source
        mappings = []
        if gvp['source'] == 'johnson':
            mappings = self.uow.data_mapping.get_mappings_for_johnson_site_id_fqr([[gvp['johnson_site_id'],
                                                                                    gvp['johnson_fqr']]])
        elif gvp['source'] == 'fieldserver':
            mappings = self.uow.data_mapping.get_mappings_for_fieldserver_site_id_offset([[gvp['fieldserver_site_id'],
                                                                                           gvp['fieldserver_offset']]])
        elif gvp['source'] == 'invensys':
            mappings = self.uow.data_mapping.get_mappings_for_invensys_site_equipment_point([[gvp['invensys_site_name'],
                                                                                              gvp['invensys_equipment_name'],
                                                                                              gvp['invensys_point_name']]])
        elif gvp['source'] == 'siemens':
            mappings = self.uow.data_mapping.get_mappings_for_siemens_meter_name([[gvp['siemens_meter_name']]])

        for mapping in mappings:
            self.logger.debug("Handling mapping for " + str(mapping['syrx_num']))
            self._handle_mapping(mapping)

    def _handle_mapping(self, mapping):
        # get the existing records by datetime
        records = self.uow.energy_records.get_all_equipment_point_records_for_syrx_num(mapping['syrx_num'])
        records_by_datetime = self._get_existing_records_by_datetime(records)

        # find the diff between the existing and the current records
        records_to_insert = self._find_new_records(mapping, records_by_datetime)

        self.logger.debug("Found " + str(len(records_to_insert)) + " for " + str(mapping['syrx_num']) + ".")

        # insert the diff
        self._insert_new_records(mapping, records_to_insert)

    @staticmethod
    def _get_existing_records_by_datetime(records):
        dict_by_date = dict((r['date'], r) for r in records)
        return dict_by_date

    @staticmethod
    def _get_all_records_by_datetime(records):
        dict_by_date = dict((r['date'], r) for r in records)
        return dict_by_date

    def _find_new_records(self, mapping, existing_records_by_datetime):
        if mapping['source'] == 'johnson':
            all_records = self.uow.global_vendor_point_records.get_all_for_johnson_point(mapping['johnson_site_id'],
                                                                                         mapping['johnson_fqr'])
        elif mapping['source'] == 'fieldserver':
            all_records = self.uow.global_vendor_point_records.get_all_for_fieldserver_point(mapping['fieldserver_site_id'],
                                                                                             mapping['fieldserver_offset'])
        elif mapping['source'] == 'invensys':
            all_records = self.uow.global_vendor_point_records.get_all_for_invensys_point(mapping['invensys_site_name'],
                                                                                          mapping['invensys_equipment_name'],
                                                                                          mapping['invensys_point_name'])
        else:
            all_records = self.uow.global_vendor_point_records.get_all_for_siemens_point(mapping['siemens_meter_name'])

        all_records_by_datetime = self._get_all_records_by_datetime(all_records)
        diff = DictDiffer(all_records_by_datetime, existing_records_by_datetime)

        # convert the set of keys to a list of the records added
        return [all_records_by_datetime[r] for r in list(diff.added())]

    def _insert_new_records(self, mapping, records):
        insert_list = []
        error_list = []

        self._populate_weatherstation_id_on_records(mapping['syrx_num'], records)
        # weather_data is a dict keyed by the weatherstation id
        try:
            weather_data = self._get_weather_data(records)
        except:
            weather_data = dict()

        for r in records:
            error_messages = []
            value = None
            equipment_point_record = None

            try:
                value = float(r["value"])
            except:
                error_messages.append("Value is not a number")

            try:
                date = r['date']
                syrx_num = mapping["syrx_num"]
                weather = None

                weather_time = date.replace(minute=0)

                if "weatherstation_id" not in r or r["weatherstation_id"] not in weather_data:
                    error_messages.append("Weatherstation not found")
                elif weather_time not in weather_data[r["weatherstation_id"]]:
                    weather_time_str = weather_time.strftime("%Y-%m-%d %H:%M:%S")
                    error_messages.append("Time " + weather_time_str + " not found in weather data")
                else:
                    weather = weather_data[r["weatherstation_id"]][weather_time]

                equipment_point_record = self.uow.energy_records.get_equipment_point_record(date, syrx_num,
                                                                                            value, weather,
                                                                                            self.date_time)
            except:
                error_messages.append("Timestamp could not be parsed")

            if len(error_messages) < 1:
                insert_list.append(equipment_point_record)
            else:
                mapping["errors"] = error_messages
                error_list.append(mapping)

        self.logger.debug("Found " + str(len(insert_list)) + " good records for " + str(mapping['syrx_num']) + ".")

        # insert the good records
        self.uow.energy_records.insert_equipment_point_records(insert_list)

        # get date range
        date_list = [x['date'] for x in insert_list]
        min_date = min(date_list)
        max_date = max(date_list)
        compiler = EnergyRecordCompiler()
        self.uow.compiled_energy_records.delete_compiled_equipment_point_records(mapping['syrx_num'], min_date, max_date)
        compiler.compile_component_point_records_by_year_span(mapping['syrx_num'], min_date, max_date)

        if len(error_list) > 0:
            # write bad records to file
            self._handle_bad_records(error_list)

    def _populate_weatherstation_id_on_records(self, syrx_num, records):
        weatherstation_ids_by_syrx_num = self.uow.component_points.get_weatherstation_ids_for_syrx_numbers([syrx_num])
        for r in records:
            if syrx_num not in weatherstation_ids_by_syrx_num:
                continue
            weatherstation_id = weatherstation_ids_by_syrx_num[syrx_num]
            r["weatherstation_id"] = weatherstation_id

    def _get_weather_data(self, records):
        weatherstation_years_to_retrieve = self._get_weatherstation_years_to_retrieve(records)
        weather_data = self._get_weather_data_records(weatherstation_years_to_retrieve)
        return weather_data

    @staticmethod
    def _get_weatherstation_years_to_retrieve(records):
        weatherstation_years_to_retrieve = defaultdict(set)
        for r in records:
            try:
                year = r['date'].year
                weatherstation_years_to_retrieve[r["weatherstation_id"]].add(year)
            except:
                pass

        return weatherstation_years_to_retrieve

    def _get_weather_data_records(self, weatherstation_years_to_retrieve):
        weather_data = dict()
        for weatherstation_id, years_set in weatherstation_years_to_retrieve.iteritems():
            years = list(years_set)

            weatherstation_data = self.uow.weather_stations.get_noaa_records(weatherstation_id, years)
            weatherstation_data = dict((d["datetimeutc"], d) for d in weatherstation_data)

            weather_data[weatherstation_id] = weatherstation_data

        return weather_data

    def _handle_bad_records(self, bad_records):
        with open(path.join(self.error_folder, "errors.log"), "a+") as bad_record_file:
            for row in bad_records:
                bad_record_file.write(json.dumps(row) + u"\n")