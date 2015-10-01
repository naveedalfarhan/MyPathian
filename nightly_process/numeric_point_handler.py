from datetime import timedelta, datetime
from compile_energy_records import EnergyRecordCompiler
from db.uow import UoW
from operator import itemgetter
import pytz


class NumericPointHandler:
    def __init__(self):
        self.uow = UoW(False)
        self.numeric_points = []
        self.numeric_points_by_code = None
        self.point_ranges = []

    def run(self):
        self._get_numeric_points()
        self._evaluate_points()
        self._compile_equipment_point_records()

    def _get_numeric_points(self):
        self.numeric_points = self.uow.component_points.get_points_by_type("NP")
        self.numeric_points_by_code = dict((p["code"].upper(), p) for p in self.numeric_points)

    def _evaluate_points(self):
        for p in self.numeric_points:
            self._evaluate_point(p)

    def _evaluate_point(self, component_point):
        # for point 237323-CP-001 get... 100000-0001-237323-CP-001, 100001-0001-237323-CP-001, etc

        equipment_points = self.uow.equipment.get_equipment_points_by_component_point_id(component_point["id"])
        for equipment_point in equipment_points:
            self._evaluate_equipment_point(equipment_point, component_point)

    def _evaluate_equipment_point(self, equipment_point, component_point):
        if "values" not in equipment_point:
            return

        syrx_num = equipment_point["syrx_num"]
        equipment_point_records = []

        values = sorted(equipment_point["values"], key=itemgetter("effective_date"))
        current_value_index = 0
        current_value = values[0]
        if len(values) > 1:
            next_value = values[1]
        else:
            next_value = None

        min_date = values[0]["effective_date"]
        if "max_date" in equipment_point:
            min_date = equipment_point["max_date"] + timedelta(minutes=15)

        max_date = pytz.UTC.localize(datetime.utcnow())

        weather_data = self._get_weather_records(syrx_num, min_date, max_date)

        date = min_date
        while date <= max_date:
            if next_value is not None and date >= next_value["effective_date"]:
                current_value = next_value
                current_value_index += 1
                if (current_value_index + 1) < len(values):
                    next_value = values[current_value_index + 1]
                else:
                    next_value = None

            value = current_value["value"]

            weather_time = date.replace(minute=0)
            weather = None
            if weather_time.year not in weather_data or weather_time not in weather_data[weather_time.year]:
                pass
                #weather_time_str = weather_time.strftime("%Y-%m-%d %H:%M:%S")
                #error_messages.append("Time " + weather_time_str + " not found in weather data")
            else:
                weather = weather_data[weather_time.year][weather_time]

            if weather is not None:
                equipment_point_record = self.uow.energy_records.get_equipment_point_record(date, syrx_num,
                                                                                            value, weather, max_date)
                equipment_point_records.append(equipment_point_record)

            if len(equipment_point_records) >= 200:
                self.uow.energy_records.insert_equipment_point_records(equipment_point_records)
                equipment_point_records = []

            date += timedelta(minutes=15)

        if len(equipment_point_records) > 0:
            self.uow.energy_records.insert_equipment_point_records(equipment_point_records)

        self.point_ranges.append({"syrx_num": equipment_point["syrx_num"],
                                  "start_date": min_date,
                                  "end_date": max_date})

    def _get_weather_records(self, syrx_num, start_date, end_date):
        start_year = start_date.year
        end_year = end_date.year

        years = [y for y in range(start_year, end_year + 1)]

        weatherstation_ids_by_syrx_num = self.uow.component_points.get_weatherstation_ids_for_syrx_numbers([syrx_num])
        if syrx_num not in weatherstation_ids_by_syrx_num:
            return []
        weatherstation_id = weatherstation_ids_by_syrx_num[syrx_num]

        weatherstation_data = dict()
        for y in years:
            weatherstation_year_data = self.uow.weather_stations.get_noaa_records(weatherstation_id, [y])
            weatherstation_data[y] = dict((d["datetimeutc"], d) for d in weatherstation_year_data)

        return weatherstation_data

    def _compile_equipment_point_records(self):
        compiler = EnergyRecordCompiler()
        for r in self.point_ranges:
            syrx_num = r["syrx_num"]
            start_date = r["start_date"]
            end_date = r["end_date"]
            self.uow.compiled_energy_records.delete_compiled_equipment_point_records(syrx_num, start_date, end_date)
            compiler.compile_component_point_records_by_year_span(syrx_num, start_date, end_date)




