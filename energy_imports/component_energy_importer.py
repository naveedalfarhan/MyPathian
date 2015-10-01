import csv
from datetime import datetime
from time import strptime, mktime, clock

from compile_energy_records import EnergyRecordCompiler
from db.uow import UoW
from dateutil import parser
import pytz
import logging


class ComponentEnergyImporter():

    def __init__(self, record_list=None):
        self.uow = UoW(None)

        self.record_list = record_list
        self.weatherstation_ids_by_syrx_num = dict()
        self.weatherstation_ids = []
        self.syrx_nums = []
        self.weather_data_by_weatherstation_id = dict()
        self.current_progress_point = 0
        self.total_progress_points = 1
        self.complete = False
        self.error = False
        self.message = ""
        self.record_targets = []

        self.invalid_rows = []

        self.calculate_progress_points()

        self.logger = logging

    def get_weather_data(self):
        self.weatherstation_ids_by_syrx_num = self.uow.component_points\
            .get_weatherstation_ids_for_syrx_numbers(self.syrx_nums)

        # keys are weatherstation ids, each value is the list of years for that particular weatherstation
        weatherstation_years = dict()
        for row in self.record_list:
            try:
                weatherstation_id = self.weatherstation_ids_by_syrx_num[row["syrx_num"]]
                if weatherstation_id not in weatherstation_years:
                    weatherstation_years[weatherstation_id] = set()

                year = row["timestamp"].year
                weatherstation_years[weatherstation_id].add(year)
            except:
                # couldn't find weatherstation for syrx num
                pass


        for weatherstation_id in weatherstation_years:
            years = list(weatherstation_years[weatherstation_id])

            weather_data = self.uow.weather_stations.get_noaa_records(weatherstation_id, years)
            weather_data = dict((d["datetimeutc"], d) for d in weather_data)

            self.weather_data_by_weatherstation_id[weatherstation_id] = weather_data

    def determine_record_targets(self):
        self.syrx_nums = set()
        syrx_num_start_dates = dict()
        syrx_num_end_dates = dict()
        for row in self.record_list:
            syrx_num = row["syrx_num"]
            self.syrx_nums.add(syrx_num)
            date = row["timestamp"]

            if syrx_num not in syrx_num_start_dates:
                syrx_num_start_dates[syrx_num] = date
            else:
                syrx_num_start_dates[syrx_num] = min(date, syrx_num_start_dates[syrx_num])

            if syrx_num not in syrx_num_end_dates:
                syrx_num_end_dates[syrx_num] = date
            else:
                syrx_num_end_dates[syrx_num] = max(date, syrx_num_end_dates[syrx_num])

        for syrx_num in self.syrx_nums:
            start_date = syrx_num_start_dates[syrx_num]
            end_date = syrx_num_end_dates[syrx_num]

            self.record_targets.append({"syrx_num": syrx_num, "start_date": start_date, "end_date": end_date})

    def delete_old_records(self):
        for target in self.record_targets:
            syrx_num = target["syrx_num"]
            start_date = target["start_date"]
            end_date = target["end_date"]
            self.uow.energy_records.delete_equipment_point_range(syrx_num, start_date, end_date)
            self.uow.compiled_energy_records.delete_compiled_equipment_point_records(syrx_num,
                                                                                     start_date, end_date)

    def calculate_progress_points(self):
        self.total_progress_points = len(self.record_list)

    def compile_records(self):
        compiler = EnergyRecordCompiler()
        for target in self.record_targets:
            syrx_num = target["syrx_num"]
            start_date = target["start_date"]
            end_date = target["end_date"]
            compiler.compile_component_point_records_by_year_span(syrx_num, start_date, end_date)

    def run(self):
        try:
            start_time = clock()
            self.logger.debug("Component point importer start")

            self.message = "Determining record targets..."
            self.logger.debug("Determining record targets")
            self.determine_record_targets()
            self.logger.debug("Determining record targets completed after " + str(clock() - start_time))

            self.message = "Deleting old records..."
            self.logger.debug("Deleting old records")
            self.delete_old_records()
            self.logger.debug("Deleting old records completed after " + str(clock() - start_time))

            #self.local_tz = pytz.timezone("America/New_York")

            self.message = "Loading weather data..."
            self.logger.debug("Getting weather data")
            self.get_weather_data()
            self.logger.debug("Get weather data completed after " + str(clock() - start_time))

            self.message = "Saving energy data..."
            self.current_progress_point += 1
            self.logger.debug("Getting records")
            self.get_records()
            self.logger.debug("Get records completed after " + str(clock() - start_time))

            self.message = "Compiling energy reports..."
            self.logger.debug("Compiling energy records")
            self.compile_records()
            self.logger.debug("Compiler completed after " + str(clock() - start_time))
            self.complete = True
            self.message = "Complete"

            self.logger.debug("Component point importer complete")
        except:
            self.logger.exception("An error occured importing energy data")
            self.error = True
            self.message = "An error has occurred."
            raise


    def get_records(self):
        energy_records = []
        imported_equipment_point_record_ids_to_delete = []

        self.logger.debug("Found " + str(len(self.record_list)) + " record(s)")
        for row in self.record_list:

            utc_date = row["timestamp"]
            record = {
                "hours_in_record": 0.25,
                "syrx_num": row["syrx_num"],
                "date": utc_date,
                "value": row["value"]
            }
            # ignore timezones for now
            #readingdatelocal = utc_date.astimezone(self.local_tz)
            readingdatelocal = utc_date
            record["local_day_of_week"] = readingdatelocal.weekday()
            record["local_hour"] = readingdatelocal.hour
            record["local_month"] = readingdatelocal.month
            record["local_year"] = readingdatelocal.year
            record["local_day_of_month"] = readingdatelocal.day

            if 13 <= readingdatelocal.hour < 18 and 6 <= readingdatelocal.month <= 8 and \
                                    0 <= readingdatelocal.weekday() <= 4:
                record["peak"] = 'peak'
            else:
                record["peak"] = 'offpeak'

            weather_time = utc_date.replace(minute=0)
            try:
                record["weather"] = self.weather_data_by_weatherstation_id[self.weatherstation_ids_by_syrx_num[row["syrx_num"]]][weather_time]
            except KeyError:
                self.invalid_rows.append(row)
                record = None

            if record is not None:
                energy_records.append(record)
                imported_equipment_point_record_ids_to_delete.append(row["id"])

            if len(energy_records) == 250:
                self.uow.energy_records.insert_equipment_point_records(energy_records)
                self.uow.data_mapping.delete_imported_equipment_point_records(imported_equipment_point_record_ids_to_delete)
                energy_records = []
                imported_equipment_point_record_ids_to_delete = []

            self.current_progress_point += 1

        self.uow.energy_records.insert_equipment_point_records(energy_records)
        self.uow.data_mapping.delete_imported_equipment_point_records(imported_equipment_point_record_ids_to_delete)