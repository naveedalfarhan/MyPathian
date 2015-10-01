import math
from db.uow import UoW
import pytz
from datetime import datetime, timedelta
import logging

class Importer:
    def __init__(self, weatherstation_id, year, start_after_date, file_path):
        self.weatherstation_id = weatherstation_id
        self.year = year
        self.start_after_date = start_after_date
        self.file_path = file_path
        self.__records_by_date = {}
        self.uow = UoW(None)

    @staticmethod
    def parse_date(date_string):
        year_part = int(date_string[0:4])
        month_part = int(date_string[4:6])
        day_part = int(date_string[6:8])
        hour_part = int(date_string[8:10])

        date = pytz.utc.localize(datetime(year_part, month_part, day_part, hour_part))

        return date

    def run(self):
        file_handle = open(self.file_path, "r")
        file_handle.readline()  # skip first line, it's a header row

        lines = file_handle.readlines()

        logging.debug("Parsing " + str(len(lines)) + " lines")
        line_num = 2
        for line in lines:
            if len(line) < 132:
                logging.warn("Incomplete line found on line " + str(line_num))
                continue
            self.__handle_line(line)

        logging.debug("Resolving guesses")
        self.__resolve_guesses()
        logging.debug("Calculating enthalpy")
        self.__calculate_enthalpy_for_records()
        logging.debug("Saving records")
        self.__save_records()

    def __handle_line(self, line):
        date_part = line[13:25]
        temp_part = line[83:87]
        dewpt_part = line[88:92]
        alt_part = line[100:105]

        record = {
            "datetimeutc": self.parse_date(date_part),
            "weatherstation_id": self.weatherstation_id,
            "localyear": self.year,
            "temp": None,
            "temp_guess": True,
            "dewpt": None,
            "dewpt_guess": True,
            "alt": None,
            "alt_guess": True,
            "enthalpy": None,
            "enthalpy_guess": True
        }

        # for all of these, the None initialized above is enough.
        # we don't need to catch the exception.
        try:
            record["alt"] = float(alt_part)
            record["alt_guess"] = False
        except:
            pass
        try:
            record["dewpt"] = float(dewpt_part)
            record["dewpt_guess"] = False
        except:
            pass
        try:
            record["temp"] = float(temp_part)
            record["temp_guess"] = False
        except:
            pass

        if record["datetimeutc"] in self.__records_by_date:
            existing_record = self.__records_by_date[record["datetimeutc"]]
            if existing_record["temp"] is None:
                existing_record["temp"] = record["temp"]
                existing_record["temp_guess"] = record["temp_guess"]
            if existing_record["dewpt"] is None:
                existing_record["dewpt"] = record["dewpt"]
                existing_record["dewpt_guess"] = record["dewpt_guess"]
            if existing_record["alt"] is None:
                existing_record["alt"] = record["alt"]
                existing_record["alt_guess"] = record["alt_guess"]
        else:
            self.__records_by_date[record["datetimeutc"]] = record

    def __resolve_guesses(self):
        records = self.__records_by_date.values()
        records.sort(key=lambda x: x["datetimeutc"])

        last_good_temp = None
        last_good_dewpt = None
        last_good_alt = None
        bad_temp_records = []
        bad_dewpt_records = []
        bad_alt_records = []

        for record in records:
            if record["temp"] is None:
                bad_temp_records.append(record)
            else:
                if len(bad_temp_records) > 0:
                    self.__average_values(last_good_temp, record, bad_temp_records, "temp")
                    bad_temp_records = []
                last_good_temp = record

            if record["dewpt"] is None:
                bad_dewpt_records.append(record)
            else:
                if len(bad_dewpt_records) > 0:
                    self.__average_values(last_good_dewpt, record, bad_dewpt_records, "dewpt")
                    bad_dewpt_records = []
                last_good_dewpt = record

            if record["alt"] is None:
                bad_alt_records.append(record)
            else:
                if len(bad_alt_records) > 0:
                    self.__average_values(last_good_alt, record, bad_alt_records, "alt")
                    bad_alt_records = []
                last_good_alt = record

        if len(bad_temp_records) > 0:
            self.__average_values(None, last_good_temp, bad_temp_records, "temp")
        if len(bad_dewpt_records) > 0:
            self.__average_values(None, last_good_dewpt, bad_dewpt_records, "dewpt")
        if len(bad_alt_records) > 0:
            self.__average_values(None, last_good_alt, bad_alt_records, "alt")

    def __calculate_enthalpy_for_records(self):
        records = self.__records_by_date.values()

        for record in records:
            record["enthalpy"] = self.calculate_enthalpy(record["temp"], record["dewpt"], record["alt"])
            record["enthalpy_guess"] = record["temp_guess"] or record["dewpt_guess"] or record["alt_guess"]

    @classmethod
    def calculate_enthalpy(cls, temp_f, dewpt_f, alt):
        # relative humidity equation taken from http://www.gorhamschaffler.com/humidity_formulas.htm and simplified
        # (5) Es=6.11*10.0**(7.5*Tc/(237.7+Tc))
        # (6) E=6.11*10.0**(7.5*Tdc/(237.7+Tdc))
        # (7) Relative Humidity(RH) in percent =(E/Es)*100
        # rh = (6.11 * 10.0**(7.5 * Tdc / (237.7 + Tdc))) / (6.11 * 10.0**(7.5 * Tc / (237.7 + Tc)))
        # rh = (10.0**(7.5 * Tdc / (237.7 + Tdc))) / (10.0**(7.5 * Tc / (237.7 + Tc)))
        # rh = 10.0**(7.5 * Tdc / (237.7 + Tdc) - 7.5 * Tc / (237.7 + Tc))
        # rh = 10.0**(7.5 * (Tdc / (237.7 + Tdc) - Tc / (237.7 + Tc)))
        # this formula is corroborated by
        # http://www.vaisala.com/Vaisala%20Documents/Application%20notes/Humidity_Conversion_Formulas_B210973EN-F.pdf

        temp_c = cls.convert_temp_f_to_c(temp_f)
        dewpt_c = cls.convert_temp_f_to_c(dewpt_f)
        e = 6.11 * 10.0**(7.5*dewpt_f/(dewpt_f + 237.7))
        es = 6.11 * 10.0**(7.5*temp_f/(temp_f + 237.7))
        rh = e/es


        # source of specific_humidity equation unknown

        x = 273.16 / (temp_c + 273.16)
        x = (-10.7959 * (1 - x)) - (2.1836 * math.log(x)) + 2.2196
        x = alt * (1 / math.e**(2.3026 * x))
        x = (rh * x)
        specific_humidity = (0.622 * x) / (alt - x)

        # enthalpy equation taken from
        # http://www.peci.org/ftguide/ftg/IntegratedOperation/IOC-Sidebars-1-3/IOC-SB3-How-To-Calculate-Enthalpy.htm
        # H = (0.24 x T) + [W x (1061 + 0.444 x T)]

        enthalpy = 0.24 * temp_f + specific_humidity * (1061 + 0.444 * temp_f)

        return enthalpy

    @staticmethod
    def convert_temp_f_to_c(temp_f):
        return (temp_f - 32) * 5 / 9

    @staticmethod
    def __average_values(first_good_record, last_good_record, bad_records, field):
        if first_good_record is None and last_good_record is None:
            raise Exception("At least one of first_good_record and last_good_record must not be None")

        if first_good_record is not None:
            first_value = first_good_record[field]
        else:
            first_value = last_good_record[field]

        if last_good_record is not None:
            last_value = last_good_record[field]
        else:
            last_value = first_good_record[field]

        value_diff = last_value - first_value

        num_samples = len(bad_records) + 1
        sample_num = 1

        for record in bad_records:
            record[field] = first_value + value_diff * sample_num / num_samples

    def __save_records(self):
        records = self.__records_by_date.values()
        if self.start_after_date:
            records = [r for r in records if r["datetimeutc"] > self.start_after_date]

        logging.info("Saving " + str(len(records)) + " records")
        print("Saving " + str(len(records)) + " records")
        batch = []
        record_num = 0
        for record in records:
            batch.append(record)
            record_num += 1
            if len(batch) >= 200:
                self.uow.weather_stations.insert_noaa_records(batch)
                logging.info("Saved " + str(record_num) + " records")
                print("Saved " + str(record_num) + " records")
                batch = []


        if len(batch) >= 0:
            self.uow.weather_stations.insert_noaa_records(batch)
            logging.info("Saved " + str(record_num) + " records")
            print("Saved " + str(record_num) + " records")
            batch = []