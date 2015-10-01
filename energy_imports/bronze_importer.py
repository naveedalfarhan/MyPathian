from datetime import datetime, timedelta
from time import strptime
from db.uow import UoW
import xlrd
from api.models.Account import Account
from api.models.Group import Group
from compile_energy_records import EnergyRecordCompiler
import dateutil
from dateutil import parser
import pytz


class BronzeImporter:
    def __init__(self, model, submission_id):
        self.group = None
        self.model = model
        self.submission_id = submission_id
        self.uow = UoW(None)

    def run(self):
        self.uow.bronze_reporting.change_submission_state(self.submission_id, "processing")

        model = self.model

        group = Group({
            "name": model["name"],
            "address": model["address"],
            "city": model["city"],
            "state": model["state"],
            "phone": model["phone"],
            "email": model["email"],
            "naics_code": model["naics"],
            "sic_code": model["sic"],
            "isRoot": True
        })

        self.uow.groups.insert(group)
        self.group = group

        if model["electricAccount"]["enabled"]:
            if model["electricAccount"]["uploadFormat"] == "grid":
                self.import_account_manual_data(model["electricAccount"],
                                                float(model["sqft"]), "electric")
            else:
                self.import_account_energy_star_file(model["electricAccount"], float(model['sqft']), "electric")
        if model["gasAccount"]["enabled"]:
            if model["gasAccount"]["uploadFormat"] == "grid":
                self.import_account_manual_data(model["gasAccount"],
                                                float(model["sqft"]), "gas")
            else:
                self.import_account_energy_star_file(model["gasAccount"], float(model['sqft']), "gas")

        self.uow.bronze_reporting.change_submission_state(self.submission_id, "completed")


    def import_account_manual_data(self, model, sqft, account_type):
        account = Account({
            "name": model["name"],
            "group_id": self.group.id,
            "type": account_type
        })
        self.uow.accounts.insert(account)

        records = self.spread_energy_data(account.id, account_type, model["timezone"], sqft, model["manualData"],
                                          model["units"])
        self.apply_weather_data(model["weatherstation_id"], records)

        years = set()
        buffer = []
        record_num = 0
        for r in records:
            years.add(r["readingdatelocal"].year)
            buffer.append(r)
            record_num += 1
            if len(buffer) == 250 or record_num == len(records):
                self.uow.energy_records.insert_many(buffer)
                buffer = []

        years = list(years)
        sorted(years)

        compiler = EnergyRecordCompiler()
        compiler.compile_energy_records_by_year_span(years[0], years[len(years) - 1], account.id)

    def import_account_energy_star_file(self, model, sqft, account_type):
        account = Account({
            "name": model["name"],
            "group_id": self.group.id,
            "type": account_type,
            "weatherstation_id": model["weatherstation_id"],
            "timezone": model["timezone"]
        })

        account.id = self.uow.accounts.insert(account)

        records = self.retrieve_excel_records(model, sqft, account)
        self.apply_weather_data(model['weatherstation_id'], records)

        years = set()
        buffer = []
        record_num = 0
        for r in records:
            years.add(r["readingdatelocal"].year)
            buffer.append(r)
            record_num += 1
            if len(buffer) == 250 or record_num == len(records):
                self.uow.energy_records.insert_many(buffer)
                buffer = []

        years = list(years)
        sorted(years)

        compiler = EnergyRecordCompiler()
        compiler.compile_energy_records_by_year_span(years[0], years[len(years) - 1], account.id)

    def retrieve_excel_records(self, model, sqft, account):
        # get the excel book, and more specifically the Meter Consumption Data sheet
        book = xlrd.open_workbook(model['file'])
        sheet = book.sheet_by_name("Meter Consumption Data")

        blank_lines_found = False
        header_found = False
        headers = []

        # set variables for the index of all of the headers for quick access when getting data
        pmm_id = 0
        meter_name = 0
        meter_type = 0
        start_date = 0
        end_date = 0
        usage = 0
        units = 0
        cost = 0

        timezone = pytz.timezone(model['timezone'])
        records = []
        for rown in range(0, sheet.nrows):
            if not sheet.row_values(rown)[0]:
                blank_lines_found = True
            else:
                if blank_lines_found and not header_found:
                    headers = sheet.row_values(rown)
                    if not headers[0]:
                        continue
                    header_found = True
                    # store the index of every header that we want
                    pmm_id = headers.index("Portfolio Manager Meter ID")
                    meter_name = headers.index("Meter Name")
                    meter_type = headers.index("Meter Type")
                    start_date = headers.index("Start Date")
                    end_date = headers.index("End Date")
                    usage = headers.index("Usage/Quantity")
                    units = headers.index("Usage Units")
                    cost = headers.index("Cost ($)")
                elif blank_lines_found and header_found:
                    row_vals = sheet.row_values(rown)
                    if row_vals[meter_name] != model['meterName']:
                        continue
                    # the module xlrd reads dates in as a floating point number, so we convert to tuple then to datetime
                    record_start_date = xlrd.xldate_as_tuple(row_vals[start_date], 0)
                    record_start_date = datetime(record_start_date[0], record_start_date[1], record_start_date[2])
                    record_start_date = timezone.normalize(timezone.localize(record_start_date))
                    record_end_date = xlrd.xldate_as_tuple(row_vals[end_date], 0)
                    record_end_date = datetime(record_end_date[0], record_end_date[1], record_end_date[2])
                    record_end_date = timezone.normalize(timezone.localize(record_end_date))
                    record_usage = float(row_vals[usage])
                    record_cost = float(row_vals[cost])
                    record_units = self.get_units(row_vals[units])

                    date_diff = record_end_date - record_start_date
                    diff_hours = date_diff.days * 24 + date_diff.seconds / 3600.0
                    energy_per_record = record_usage / diff_hours
                    cost_per_record = record_cost / record_usage

                    record_date = record_start_date
                    while record_date < record_end_date:
                        record_date_utc = record_date.astimezone(pytz.utc)
                        record = {
                            'account_id': account.id,
                            'energy': {
                                'btu': 0
                            },
                            'hours_in_record': 1,
                            "price_normalization": cost_per_record,
                            "readingdatelocal": record_date,
                            "readingdateutc": record_date_utc,
                            "size_normalization": sqft,
                            "type": account.type,
                            "local_day_of_week": record_date.weekday(),
                            "local_hour": record_date.hour,
                            "local_month": record_date.month,
                            "local_year": record_date.year,
                            "local_day_of_month": record_date.day
                        }
                        if 13 <= record["local_hour"] < 18 and 6 <= record["local_month"] <= 8 \
                                and 0 <= record["local_day_of_week"] <= 4:
                            record["peak"] = 'peak'
                        else:
                            record["peak"] = 'offpeak'

                        if account.type == "electric":
                            if record_units == "kwh":
                                record["energy"]["btu"] = energy_per_record * 3412.32
                            elif record_units == "mwh":
                                record["energy"]["btu"] = energy_per_record * 3412140
                            elif record_units == "kbtu":
                                record["energy"]["btu"] = energy_per_record * 1000
                            elif record_units == "mmbtu":
                                record["energy"]["btu"] = energy_per_record * 1000000
                            elif record_units == "gj":
                                record["energy"]["btu"] = energy_per_record * 3412.32 / 0.0036
                            record["energy"]["kwh"] = record["energy"]["btu"] / 3412.32
                            record["energy"]["kvar"] = 0
                        elif account.type == "gas":
                            if record_units == "mmcf":
                                record["energy"]["btu"] = energy_per_record * 1025000000
                            if record_units == "mcf":
                                record["energy"]["btu"] = energy_per_record * 1025000
                            elif record_units == "ccf":
                                record["energy"]["btu"] = energy_per_record * 102500
                            elif record_units == "cf":
                                record["energy"]["btu"] = energy_per_record * 1025
                            elif record_units == "cm":
                                # 2.54 cm/in * 0.01 m/cm * 12 in/ft = 0.3048 m/ft
                                # (0.3048 m/ft) ** 3 = 0.028316846592 (m/ft) ** 3
                                # (? m ** 3) / 0.028316846592 (m/ft) ** 3 = ? (ft ** 3) == ? cf
                                record["energy"]["btu"] = energy_per_record / 0.028316846592 * 1.025
                            elif record_units == "kbtu":
                                record["energy"]["btu"] = energy_per_record * 1000
                            elif record_units == "mmbtu":
                                record["energy"]["btu"] = energy_per_record * 1000000
                            elif record_units == "therm":
                                record["energy"]["btu"] = energy_per_record * 100000
                            elif record_units == "gj":
                                record["energy"]["btu"] = energy_per_record * 3412.32 / 0.0036

                        records.append(record)
                        record_date += timedelta(hours=1)
        return records

    def get_units(self, value):
        # figure out what units to use by looking at the first few letters
        lower_value = value.lower()
        if value[:3] == "kcf":
            return "mcf"
        if value[:3] == "mcf":
            return "mmcf"
        if value[:3] == "kwh":
            return "kwh"
        if value[:4] == "kbtu":
            return "kbtu"
        if value[:3] == "mwh":
            return "mwh"
        if value[:4] == "mbtu":
            return "mmbtu"
        if value[:3] == "the":
            # therms
            return "therm"
        if value[:2] == "cf":
            return "cf"
        if value[:3] == "ccf":
            return "ccf"
        if value[:2] == "GJ":
            return "gj"
        if value[:3] == "Cub":
            # cubic meters
            return "cm"

    def spread_energy_data(self, account_id, account_type, timezone_name, sqft, data, units):
        records = []
        timezone = pytz.timezone(timezone_name)

        for data_record in data:
            start_date = dateutil.parser.parse(data_record["StartDate"])
            start_date = datetime(start_date.year, start_date.month, start_date.day)
            start_date = timezone.normalize(timezone.localize(start_date))
            end_date = dateutil.parser.parse(data_record["EndDate"])
            end_date = datetime(end_date.year, end_date.month, end_date.day)
            end_date = timezone.normalize(timezone.localize(end_date))
            usage = float(data_record["Usage"])
            cost = float(data_record["Cost"])

            date_diff = end_date - start_date
            diff_hours = date_diff.days * 24 + date_diff.seconds / 3600.0
            energy_per_record = usage / diff_hours
            cost_per_record = cost / usage

            record_date = start_date
            while record_date < end_date:
                record_date_utc = record_date.astimezone(pytz.utc)
                record = {
                    "account_id": account_id,
                    "energy": {
                        "btu": 0
                    },
                    "hours_in_record": 1,
                    "price_normalization": cost_per_record,
                    "readingdatelocal": record_date,
                    "readingdateutc": record_date_utc,
                    "size_normalization": sqft,
                    "type": account_type,
                    "local_day_of_week": record_date.weekday(),
                    "local_hour": record_date.hour,
                    "local_month": record_date.month,
                    "local_year": record_date.year,
                    "local_day_of_month": record_date.day
                }

                if 13 <= record["local_hour"] < 18 and 6 <= record["local_month"] <= 8 \
                        and 0 <= record["local_day_of_week"] <= 4:
                    record["peak"] = 'peak'
                else:
                    record["peak"] = 'offpeak'

                if account_type == "electric":
                    if units == "kwh":
                        record["energy"]["btu"] = energy_per_record * 3412.32
                    elif units == "mwh":
                        record["energy"]["btu"] = energy_per_record * 3412140
                    elif units == "kbtu":
                        record["energy"]["btu"] = energy_per_record * 1000
                    elif units == "mmbtu":
                        record["energy"]["btu"] = energy_per_record * 1000000
                    elif units == "gj":
                        record["energy"]["btu"] = energy_per_record * 3412.32 / 0.0036
                    record["energy"]["kwh"] = record["energy"]["btu"] / 3412.32
                    record["energy"]["kvar"] = 0
                elif account_type == "gas":
                    if units == "mcf":
                        record["energy"]["btu"] = energy_per_record * 1025000
                    elif units == "ccf":
                        record["energy"]["btu"] = energy_per_record * 102500
                    elif units == "cf":
                        record["energy"]["btu"] = energy_per_record * 1025
                    elif units == "cm":
                        # 2.54 cm/in * 0.01 m/cm * 12 in/ft = 0.3048 m/ft
                        # (0.3048 m/ft) ** 3 = 0.028316846592 (m/ft) ** 3
                        # (? m ** 3) / 0.028316846592 (m/ft) ** 3 = ? (ft ** 3) == ? cf
                        record["energy"]["btu"] = energy_per_record / 0.028316846592 * 1.025
                    elif units == "kbtu":
                        record["energy"]["btu"] = energy_per_record * 1000
                    elif units == "mmbtu":
                        record["energy"]["btu"] = energy_per_record * 1000000
                    elif units == "therm":
                        record["energy"]["btu"] = energy_per_record * 100000
                    elif units == "gj":
                        record["energy"]["btu"] = energy_per_record * 3412.32 / 0.0036

                records.append(record)
                record_date += timedelta(hours=1)

        return records

    def apply_weather_data(self, weatherstation_id, records):
        years = set()

        for r in records:
            year = r["readingdateutc"].year
            years.add(year)

        weather_data = self.uow.weather_stations.get_noaa_records(weatherstation_id, years)
        weather_data = dict((d["datetimeutc"], d) for d in weather_data)

        for r in records:
            year = r["readingdateutc"].year
            month = r["readingdateutc"].month
            day = r["readingdateutc"].day
            hour = r["readingdateutc"].hour
            weather_date = datetime(year, month, day, hour, tzinfo=pytz.utc)

            if weather_date in weather_data:
                r["weather"] = weather_data[weather_date]