import csv
from datetime import datetime
from time import strptime, mktime, clock
import math

from api.models.EnergyRecord import EnergyRecord
from compile_energy_records import EnergyRecordCompiler
from db.uow import UoW
from energy_imports import duke_pre_processor
from dateutil import parser
import pytz
import logging


class EnergyImporter():

    def __init__(self, account_id=None, uploaded_file_handle=None, uploaded_file_type=None):
        self.uow = UoW(None)

        self.account_id = account_id
        self.uploaded_file_handle = uploaded_file_handle
        self.uploaded_file_type = uploaded_file_type
        self.reader = csv.reader(self.uploaded_file_handle)
        self.weatherstation_id = None
        self.energy_units = None
        self.weather_data = None
        self.start_year = None
        self.end_year = None
        self.current_progress_point = 0
        self.total_progress_points = 1
        self.complete = False
        self.error = False
        self.message = ""
        self.forced_hours_in_record = None

        self.uploaded_file_handle.seek(0)
        self.calculate_progress_points()

    def get_normalizations(self):
        self.price_normalizations = self.uow.price_normalizations.get_all_by_account(self.account_id)
        self.price_norm_dates = map(lambda n: n["effective_date"], self.price_normalizations)
        self.price_norm_dict = dict((n["effective_date"], n["value"]) for n in self.price_normalizations)

        self.size_normalizations = self.uow.size_normalizations.get_all_by_account(self.account_id)
        self.size_norm_dates = map(lambda n: n["effective_date"], self.size_normalizations)
        self.size_norm_dict = dict((n["effective_date"], n["value"]) for n in self.size_normalizations)

    def get_weather_data(self):
        years = set()

        for row in self.reader:
            year = datetime.fromtimestamp(mktime(strptime(row[0], "%Y-%m-%d %H:%M"))).year
            years.add(year)

        index_query = []
        for entry in years:
            index_query.append([self.weatherstation_id, entry])
        years = list(years)

        weather_data = self.uow.weather_stations.get_noaa_records(self.weatherstation_id, years)
        self.weather_data = dict((d["datetimeutc"], d) for d in weather_data)

    def delete_old_records(self):
        start_date = None
        end_date = None
        for row in self.reader:
            date = pytz.utc.localize(datetime.fromtimestamp(mktime(strptime(row[0], "%Y-%m-%d %H:%M"))))
            if start_date is None:
                start_date = date
            else:
                start_date = min(date, start_date)
            if end_date is None:
                end_date = date
            else:
                end_date = max(date, end_date)
        self.uow.energy_records.delete_range(self.account_id, start_date, end_date)
        self.uow.compiled_energy_records.delete_compiled_records(self.account_id, start_date, end_date)


    def get_energy_units(self):
        for row in self.reader:
            self.energy_units = []
            for r in xrange(1, len(row), 1):
                if row[r].lower() == 'kvarh':
                    row[r] = 'kvar'
                self.energy_units.append(row[r].lower())
            return

    def get_effective_size_normalization(self, date):
        try:
            prior_size_normalization_dates = [item for item in self.size_norm_dates if item <= date]
            prior_size_normalization_dates.sort(reverse=True)
            effective_date = prior_size_normalization_dates[0]
            effective_size_normalization = self.size_norm_dict[effective_date]
            return effective_size_normalization
        except:
            return None

    def get_effective_price_normalization(self, date):
        try:
            prior_price_normalization_dates = [item for item in self.price_norm_dates if item <= date]
            prior_price_normalization_dates.sort(reverse=True)
            effective_date = prior_price_normalization_dates[0]
            effective_price_normalization = self.price_norm_dict[effective_date]
            return effective_price_normalization
        except:
            return None

    def calculate_progress_points(self):
        num_rows = 0
        for _ in self.reader:
            num_rows += 1

        self.total_progress_points = num_rows

    def run(self):
        try:
            start_time = clock()
            logging.info("Start importer")
            self.uploaded_file_handle.seek(0)
            if self.uploaded_file_type == "duke":
                self.message = "Running pre processor..."
                logging.info("Running pre processor")
                new_file_handle = duke_pre_processor.run(self.uploaded_file_handle)
                logging.info("Preprocessor completed after " + str(clock() - start_time))
                self.uploaded_file_handle.close()
                self.uploaded_file_handle = new_file_handle
                self.reader = csv.reader(self.uploaded_file_handle)

            self.message = "Deleting old records..."
            self.uploaded_file_handle.seek(0)
            self.uploaded_file_handle.readline()
            logging.info("Deleting old records")
            self.delete_old_records()
            logging.info("Deleting old records completed after " + str(clock() - start_time))

            self.local_tz = pytz.timezone("America/New_York")
            self.uploaded_file_handle.seek(0)



            self.get_normalizations()


            account_info = self.uow.accounts.get_by_id(self.account_id)
            self.account_type = account_info.type.lower()
            self.weatherstation_id = account_info.weatherstation_id

            self.get_energy_units()

            self.message = "Loading weather data..."
            self.uploaded_file_handle.seek(0)
            self.uploaded_file_handle.readline()
            logging.info("Getting weather data")
            self.get_weather_data()
            logging.info("Get weather data completed after " + str(clock() - start_time))

            self.message = "Saving energy data..."
            self.uploaded_file_handle.seek(0)
            self.uploaded_file_handle.readline()
            self.current_progress_point += 1
            logging.info("Getting records")
            self.get_records()
            logging.info("Get records completed after " + str(clock() - start_time))

            self.message = "Compiling energy reports..."
            compiler = EnergyRecordCompiler()
            logging.info("Compiling energy records")
            compiler.compile_energy_records_by_year_span(self.start_year, self.end_year, self.account_id)
            logging.info("Compiler completed after " + str(clock() - start_time))
            self.current_progress_point = self.total_progress_points
            self.complete = True
            self.message = "Complete"
        except:
            logging.exception("An error occured importing energy data")
            self.error = True
            self.message = "An error has occurred."
            raise


    def get_records(self):
        energy_records = []
        first_record_applied = False
        first_record = None
        first_row = None
        last_line_time = None
        for row in self.reader:
            record = EnergyRecord()
            try:
                del record.id
            except:
                pass
            record.account_id = self.account_id
            record.create_source = self.uploaded_file_handle.name
            line_date = pytz.utc.localize(parser.parse(row[0]))
            record.readingdateutc = line_date
            record.readingdatelocal = line_date.astimezone(self.local_tz)
            record.local_day_of_week = record.readingdatelocal.weekday()
            record.local_hour = record.readingdatelocal.hour
            record.local_month = record.readingdatelocal.month
            record.local_year = record.readingdatelocal.year
            record.local_day_of_month = record.readingdatelocal.day
            record.type = self.account_type
            if 13 <= record.local_hour < 18 and 6 <= record.local_month <= 8 and 0 <= record.local_day_of_week <= 4:
                record.peak = 'peak'
            else:
                record.peak = 'offpeak'

            if self.start_year is None:
                self.start_year = line_date.year
            if self.end_year is None:
                self.end_year = line_date.year

            self.start_year = min(self.start_year, line_date.year)
            self.end_year = max(self.end_year, line_date.year)

            record.price_normalization = self.get_effective_price_normalization(line_date)
            if record.price_normalization is None:
                record.price_normalization = 1

            record.size_normalization = self.get_effective_size_normalization(line_date)
            if record.size_normalization is None:
                record.size_normalization = 1

            weather_time = line_date.replace(minute=0)
            if weather_time in self.weather_data:
                record.weather = self.weather_data[weather_time]
            else:
                record.weather = {}

            if last_line_time:
                if self.forced_hours_in_record:
                    record.hours_in_record = self.forced_hours_in_record
                else:
                    record.hours_in_record = (line_date - last_line_time).total_seconds() / 3600
                last_line_time = line_date
            else:
                last_line_time = line_date

            if self.account_type == "electric":
                record.energy = self.get_electric_values(row, record.hours_in_record)
            else:
                record.energy = self.get_gas_values(row)

            if not first_record_applied and first_record:
                first_record.hours_in_record = record.hours_in_record
                if self.account_type == "electric":
                    first_record.energy = self.get_electric_values(first_row, first_record.hours_in_record)
                else:
                    first_record.energy = self.get_gas_values(first_row)
                energy_records.append(first_record.__dict__)
                first_record_applied = True
                energy_records.append(record.__dict__)
            elif not first_record:
                first_record = record
                first_row = row
            else:
                energy_records.append(record.__dict__)

            if len(energy_records) % 250 == 0:
                self.uow.energy_records.insert_many(energy_records)
                energy_records = []

            self.current_progress_point += 1

        self.uow.energy_records.insert_many(energy_records)

    def get_electric_values(self, row, hours_in_record):
        if hours_in_record:
            energy_dict = {}
            for i in xrange(0, len(self.energy_units), 1):
                energy_dict[self.energy_units[i]] = float(row[i + 1])
                if 'kwh' in energy_dict and 'kqh' in energy_dict and 'kvar' not in energy_dict:
                    kwh = float(energy_dict['kwh'])
                    kqh = float(energy_dict['kqh'])
                    energy_dict['kvar'] = (kqh * 2 - kwh) / math.sqrt(3)

                if 'kwh' in energy_dict and 'kvar' in energy_dict and 'kva' not in energy_dict:
                    kwh = float(energy_dict['kwh'])
                    kvar = float(energy_dict['kvar'])
                    energy_dict['kva'] = math.sqrt(math.pow(kwh, 2) + math.pow(kvar, 2))

                if 'kwh' in energy_dict and 'kva' in energy_dict and 'pf' not in energy_dict:
                    kwh = float(energy_dict['kwh'])
                    kva = float(energy_dict['kva'])
                    if kva == 0:
                        energy_dict['pf'] = kva
                    else:
                        energy_dict['pf'] = kwh / kva
                if 'kwh' in energy_dict:
                    energy_dict['btu'] = float(energy_dict['kwh']) * 3412.32
                    energy_dict['demand'] = energy_dict['kwh'] / hours_in_record
                    energy_dict['kvar'] = 0
            return energy_dict
        else:
            return {}

    def get_gas_values(self, row):
        energy_dict = {}
        for i in xrange(0, len(self.energy_units), 1):
            energy_dict[self.energy_units[i]] = float(row[i + 1])
            if 'mcf' in energy_dict:
                energy_dict['btu'] = float(energy_dict['mcf']) * 1025000
        return energy_dict

if "__main__" == __name__:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename="noaa_importer.log", level=logging.DEBUG)
    EnergyImporter.run("01df1f50-5997-4d67-9f6a-4b347382db5f", "sample pathian format.csv")