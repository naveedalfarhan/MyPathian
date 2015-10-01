import pyodbc
from db.uow import UoW
import rethinkdb


class ImportWeatherStations:
    def __init__(self):
        self.uow = UoW(rethinkdb.connect("localhost",016))
        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=PathianDBNet;integrated security=True")

    def import_weatherstations(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT Name, USAF, WBAN
            FROM Weatherstations
            """)

        existing_weatherstations = self.uow.weather_stations.get_all_list()
        existing_weatherstations = dict((ws["name"], ws) for ws in existing_weatherstations)
        weatherstations = []
        for row in cursor:
            ws = {
                "name": row[0],
                "usaf": str(row[1]),
                "wban": str(row[2]),
                "years": []
            }
            if row[0] not in existing_weatherstations:
                weatherstations.append(ws)

        self.uow.weather_stations.insert_many(weatherstations)

if __name__ == "__main__":
    importer = ImportWeatherStations()
    importer.import_weatherstations()
