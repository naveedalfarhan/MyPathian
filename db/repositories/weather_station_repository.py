from datetime import datetime
from api.models.WeatherStation import WeatherStation
import pytz
import rethinkdb as r


class WeatherStationRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.weatherstations

    def get_all(self, query_parameters=None, raw=False):
        if query_parameters is None:
            weatherstations = self.uow.run_list(self.table)
            if not raw:
                weatherstations = [WeatherStation(ws) for ws in weatherstations]
            return weatherstations
        else:
            query_result = self.uow.apply_query_parameters(self.table, query_parameters)
            for ws in query_result.data:
                ws["years"].sort()
                ws["years"] = ", ".join([str(year) for year in ws["years"]])
            return query_result

    def get_weatherstation_years(self, ws_id):
        years = self.uow.run_list(self.uow.tables.noaa_records
                                  .between([ws_id, 0], [ws_id, 9999], index="weatherstation_year")
                                  .group(index="weatherstation_year")
                                  .count())
        years = [str(x[1]) for x in years]

        return years

    def get_all_list(self):
        return self.uow.run_list(self.table.order_by(index="name"))

    def get_by_id(self, ws_id):
        ws_raw = self.uow.run(self.table.get(ws_id))
        if ws_raw is None:
            return None
        ws = WeatherStation(ws_raw)
        return ws

    def insert(self, ws):
        try:
            del ws.id
        except AttributeError:
            pass
        result = self.uow.run(self.table.insert(ws.__dict__))
        ws.id = result["generated_keys"][0]

    def insert_many(self, weatherstations):
        self.uow.run(self.table.insert(weatherstations))

    def update(self, ws):
        self.uow.run(self.table.get(ws.id).update(ws.__dict__))

    def delete(self, ws_id):
        self.uow.run(self.table.get(ws_id).delete())

    def get_noaa_records(self, ws_id, years):
        index_query = []
        for entry in years:
            index_query.append([ws_id, entry])

        weather_data = self.uow.run_list(self.uow.tables.noaa_records.get_all(*index_query, index='weatherstation_year'))
        for record in weather_data:
            record["enthalpy"] = round(record["enthalpy"] * 5) / 5
        return weather_data

    def get_noaa_records_multi(self, index_query):
        weather_data = self.uow.run_list(self.uow.tables.noaa_records.get_all(*index_query, index='weatherstation_year'))
        return weather_data

    def insert_noaa_records(self, records):
        self.uow.run(self.uow.tables.noaa_records.insert(records, durability="hard"))

    def get_last_record_time(self, weatherstation_id, year):
        first_date_of_year = pytz.utc.localize(datetime(year, 1, 1))
        first_date_of_next_year = pytz.utc.localize(datetime(year + 1, 1, 1))

        try:
            start_after_date = self.uow.run_list(self.uow.tables.noaa_records
                                                 .between([weatherstation_id, first_date_of_year],
                                                          [weatherstation_id, first_date_of_next_year],
                                                          right_bound="open",
                                                          index="weatherstation_date")
                                                 .order_by(index=r.desc("weatherstation_date"))
                                                 .limit(1))[0]["datetimeutc"]
            return start_after_date
        except:
            return None
