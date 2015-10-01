import pyodbc
import tempfile
from time import sleep
from api.models.import_thread import ImportThread
from db.uow import UoW
from energy_imports.importer import EnergyImporter
import os


class ImportAccountEnergyRecords:
    def __init__(self):
        self.uow = UoW(None)
        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=PathianDBNet;integrated security=True")

    def import_electric_records(self, account_id, sqlserver_account_id, year):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT e.ReadingDateUTC, e.Kwh, e.Kvar, e.CreateSource, e.CreateDate,
            e.LocalYear, e.LocalMonth, e.LocalDayOfWeek, e.LocalHour, e.HoursInRecord, e.ReadingDateLocal
            FROM ElectricRecords e
            WHERE e.AccountId = ? AND e.LocalYear = ?
            ORDER BY e.ReadingDateUTC
            """, [sqlserver_account_id, year])

        temp_file = tempfile.TemporaryFile()

        temp_file.write("Date,kwh,kvar\n")
        for row in cursor:
            date_string = row[0].strftime("%Y-%m-%d %H:%M")
            temp_file.write(date_string + "," + str(row[1]) + "," + str(row[2]) + "\n")

        temp_file.seek(0)

        self.import_from_file(temp_file)

    def import_gas_records(self, account_id, sqlserver_account_id, year):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT g.ReadingDateUTC, g.Mcf, g.CreateSource, g.CreateDate,
            g.LocalYear, g.LocalMonth, g.LocalDayOfWeek, g.LocalHour, g.ReadingDateLocal
            FROM GasRecords g
            WHERE g.AccountId = ? AND g.LocalYear = ?
            ORDER BY g.ReadingDateUTC
            """, [sqlserver_account_id, year])

        temp_file = tempfile.TemporaryFile()

        temp_file.write("Date,mcf\n")
        for row in cursor:
            date_string = row[0].strftime("%Y-%m-%d %H:%M")
            temp_file.write(date_string + "," + str(row[1]) + "\n")

        temp_file.seek(0)

        self.import_from_file(account_id, temp_file)

    def import_from_file(self, account_id, file_handle):

        energy_importer = EnergyImporter(account_id, file_handle)
        energy_importer.forced_hours_in_record = 1


        import_thread = ImportThread(energy_importer)
        import_thread.start()

        while not energy_importer.complete and not energy_importer.error:
            cp = energy_importer.current_progress_point
            tp = energy_importer.total_progress_points
            percent = round(cp / tp * 100)
            print str(cp) + "/" + str(tp) + " " + str(percent) + "%"
            sleep(5)

        file_handle.close()


if __name__ == "__main__":
    importer = ImportAccountEnergyRecords()
    importer.import_gas_records("fb98569b-74ab-4f73-8b55-e3d206cdbbcc", 19, 2010)