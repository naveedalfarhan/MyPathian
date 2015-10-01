import uuid
import pyodbc
from db.uow import UoW
import pytz
from tzlocal import get_localzone


class EnergyRecordImporter:

    def __init__(self):
        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=PathianDBNet;integrated security=True")
        self.account_dict = {}
        self.group_dict = {}
        self.uow = UoW(None)

    def load_accounts(self):
        accounts = self.uow.accounts.get_all()
        for account in accounts:
            if "old_id" in account:
                self.account_dict[account["old_id"]] = account["id"]
        print("accounts loaded")

    def load_groups(self):
        accounts = self.uow.accounts.get_all()
        for a in accounts:
            if "group_id" in a and "old_id" in a:
                g = self.uow.groups.get_group_raw_by_id(a["group_id"])
                self.group_dict[a["old_id"]] = g["name"]

    def import_electric_data(self):
        cursor = self.conn.cursor()

        cursor.execute("""SELECT e.Id, e.AccountId, e.ReadingDateUTC, e.Kwh, e.Kvar, e.Kva, e.Pf, e.CreateSource, e.CreateDate,
	e.LocalYear, e.LocalMonth, e.LocalDayOfWeek, e.LocalHour, e.HoursInRecord, e.ReadingDateLocal,
	r.DateTimeUTC, r.TempF, r.DewptF, r.Alt, r.Enthalpy, s.Value, p.Value as pValue, g.NaicsCodeCode, g.SicCodeCode
  FROM ElectricRecords e
  INNER JOIN Accounts a on e.AccountId = a.Id
  INNER JOIN NOAARecords r on r.WeatherStationId = a.WeatherStationId AND dateadd(hour,datediff(hour,0,ReadingDateUTC),0) = r.DateTimeUTC
  INNER JOIN SizeNormalizations s on e.AccountId = s.AccountId
  INNER JOIN PriceNormalizations p on e.AccountId = p.AccountId
  INNER JOIN Groups g on a.GroupId = g.Id
  WHERE a.GroupId = 330939 AND e.LocalYear = 2005
 """)

        energy_records = []
        counter = 0
        local_tz = get_localzone()

        for row in cursor:
            new_id = str(uuid.uuid4())

            utc_time = pytz.UTC.localize(row.ReadingDateUTC)
            create_date = local_tz.localize(row.CreateDate)
            utc_noaa_time = pytz.UTC.localize(row.DateTimeUTC)
            local_date = local_tz.localize(row.ReadingDateLocal)

            new_energy_record = {"id": new_id, "old_account_id": row.AccountId, "readingdateutc": utc_time,
                                 "create_source": row.CreateSource,
                                 "create_date": create_date, "local_year": row.LocalYear, "local_month": row.LocalMonth,
                                 "local_day_of_week": row.LocalDayOfWeek, "local_hour": row.LocalHour,
                                 'local_day_of_month': local_date.day,
                                 "hours_in_record": 0.25,
                                 'naics_code': row.NaicsCodeCode, 'sic_code': row.SicCodeCode,
                                 "type": "Electric",
                                 "energy": {"kwh": row.Kwh, "kvar": row.Kvar, "kva": row.Kva, "pf": row.Pf,
                                            "btu": float(row.Kwh) * 3412.32, 'demand': row.Kwh / 0.25},
                                 "weather": {"temp": row.TempF, "dewpt": row.DewptF, "alt": row.Alt,
                                             "enthalpy": row.Enthalpy,
                                             "datetimeutc": utc_noaa_time}, "price_normalization": row.pValue,
                                 "size_normalization": row.Value}

            if row.AccountId in self.account_dict:
                new_energy_record["account_id"] = self.account_dict[row.AccountId]

            if row.AccountId in self.group_dict:
                new_energy_record["group_name"] = self.group_dict[row.AccountId]

            if 13 <= row.LocalHour <= 18 and row.LocalMonth >= 6 and row.LocalMonth <= 8:
                new_energy_record['peak'] = 'peak'
            else:
                new_energy_record['peak'] = 'offpeak'

            energy_records.append(new_energy_record)

            if len(energy_records) == 1000:
                self.uow.energy_records.insert_many(energy_records)
                energy_records = []
                counter += 1000
                print ("imported " + str(counter) + " energy records")

        if len(energy_records) > 0:
            self.uow.energy_records.insert_many(energy_records)
            counter += len(energy_records)
            print ("imported " + str(counter) + " energy records")

    def import_gas_data(self):
        cursor = self.conn.cursor()

        cursor.execute("""SELECT e.Id, e.AccountId, e.ReadingDateUTC, e.Mcf, e.CreateSource, e.CreateDate,
	e.LocalYear, e.LocalMonth, e.LocalDayOfWeek, e.LocalHour, e.ReadingDateLocal,
	r.DateTimeUTC, r.TempF, r.DewptF, r.Alt, r.Enthalpy, s.Value, p.Value as pValue, g.NaicsCodeCode
  FROM GasRecords e
  INNER JOIN Accounts a on e.AccountId = a.Id
  INNER JOIN NOAARecords r on r.WeatherStationId = a.WeatherStationId AND dateadd(hour,datediff(hour,0,ReadingDateUTC),0) = r.DateTimeUTC,
  INNER JOIN SizeNormalizations s on e.AccountId = s.AccountId
  INNER JOIN PriceNormalizations p on e.AccountId = p.AccountId
  INNER JOIN Groups g on a.GroupId = g.Id
  WHERE a.GroupId = 330939 AND e.LocalYear = 2007
 """)

        energy_records = []
        counter = 0
        local_tz = get_localzone()

        for row in cursor:
            new_id = str(uuid.uuid4())

            utc_time = pytz.UTC.localize(row.ReadingDateUTC)
            create_date = local_tz.localize(row.CreateDate)
            utc_noaa_time = pytz.UTC.localize(row.DateTimeUTC)
            local_date = local_tz.localize(row.ReadingDateLocal)

            new_energy_record = {"id": new_id, "old_account_id": row.AccountId, "readingdateutc": utc_time,
                                 "create_source": row.CreateSource,
                                 "create_date": create_date, "local_year": row.LocalYear, "local_month": row.LocalMonth,
                                 'local_day_of_month': local_date.day,
                                 "local_day_of_week": row.LocalDayOfWeek, "local_hour": row.LocalHour,
                                 "type": "Gas", "energy": {"mcf": row.Mcf, "btu": float(row.Mcf) * 1025000},
                                 "weather": {"temp": row.TempF, "dewpt": row.DewptF, "alt": row.Alt,
                                             "enthalpy": row.Enthalpy,
                                             "datetimeutc": utc_noaa_time}, "size_normalization": row.Value,
                                 "price_normalization": row.pValue}

            if row.AccountId in self.account_dict:
                new_energy_record["account_id"] = self.account_dict[row.AccountId]

            if row.AccountId in self.group_dict:
                new_energy_record["group_name"] = self.group_dict[row.AccountId]

            if 13 <= row.LocalHour <= 18 and row.LocalMonth >= 6 and row.LocalMonth <= 8:
                new_energy_record['peak'] = 'peak'
            else:
                new_energy_record['peak'] = 'offpeak'

            energy_records.append(new_energy_record)

            if len(energy_records) == 500:
                self.uow.energy_records.insert_many(energy_records)
                energy_records = []
                counter += 500
                print ("imported " + str(counter) + " energy records")

        if len(energy_records) > 0:
            self.uow.energy_records.insert_many(energy_records)
            counter += len(energy_records)
            print ("imported " + str(counter) + " energy records")


if __name__ == "__main__":
    importer = EnergyRecordImporter()
    importer.load_accounts()
    importer.load_groups()
    importer.import_electric_data()