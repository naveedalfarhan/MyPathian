import copy
import datetime
from itertools import groupby
from compile_energy_records import EnergyRecordCompiler
from db.uow import UoW
from function_parser import FunctionParser
from function_parser.evaluator import Evaluator
import pytz


class CalculatedPointHandler:
    def __init__(self):
        self.uow = UoW(False)
        self.calculated_points = []
        self.calculated_points_by_code = dict()
        self.points_by_component_id = dict()
        self.safe_points = []
        self.evaluated_point_codes = []
        self.point_ranges = []

    def run(self):
        self._get_calculated_points()
        self._build_dependencies_list()
        self._build_safe_points_list()
        self._evaluate_points()
        self._compile_equipment_point_records()

    def _get_calculated_points(self):
        self.calculated_points = self.uow.component_points.get_points_by_type("CP")
        self.calculated_points_by_code = dict((p["code"].upper(), p) for p in self.calculated_points)

    def _build_dependencies_list(self):
        for point in self.calculated_points:
            component_points = self._get_points_for_component_id(point["component_id"])
            component_points_by_code = dict((p["code"].upper(), p) for p in component_points)

            try:
                expression_tree = FunctionParser.parse(point["formula"])
            except:
                # invalid formula
                point['invalid'] = True
                continue

            point["expression_tree"] = expression_tree
            point["parameters"] = []
            point["dependencies"] = []
            point["parameter_codes"] = []
            for identifier_name in expression_tree["identifier_names"]:
                if identifier_name not in component_points_by_code:
                    continue
                identifier_point = component_points_by_code[identifier_name]
                point["parameters"].append({"name": identifier_name, "point_id": identifier_point["id"]})
                point["parameter_codes"].append(identifier_name)

                if identifier_point["point_type"] == "CP":
                    point["dependencies"].append(identifier_name)

    def _build_safe_points_list(self):
        self.safe_points = [point for point in self.calculated_points if self._is_point_safe(point["code"].upper())]

    def _evaluate_points(self):
        for point in self.safe_points:
            self._evaluate_point_tree(point)

    def _evaluate_point_tree(self, point):
        if point["code"].upper() in self.evaluated_point_codes:
            return

        for dependency_point_code in point["dependencies"]:
            if dependency_point_code not in self.evaluated_point_codes:
                dependency_point = self.calculated_points_by_code[dependency_point_code]
                self._evaluate_point_tree(dependency_point)

        self._evaluate_point(point)

        self.evaluated_point_codes.append(point["code"].upper())

    def _evaluate_point(self, point):
        # for point 237323-CP-001 get... 100000-0001-237323-CP-001, 100001-0001-237323-CP-001, etc
        # get the component id's for the point code
        component_points_for_code = self.uow.component_points.get_points_by_code(point['code'])
        point_ids = map(lambda x: x['id'], component_points_for_code)
        equipment_points = self.uow.equipment.get_equipment_points_by_component_point_ids(point_ids)
        for equipment_point in equipment_points:
            self._evaluate_equipment_point(equipment_point, point)

    def _evaluate_equipment_point(self, equipment_point, component_point):
        same_component_equipment_points = self.uow.equipment.get_equipment_points_by_equipment_id_component_id(
            equipment_point["equipment_id"], equipment_point["component_id"])

        parameter_points = [x for x in same_component_equipment_points
                            if x["point_code"].upper() in component_point["parameter_codes"]]

        min_date, max_date = self._get_date_range_for_equipment_points(parameter_points)

        if min_date is None or max_date is None:
            return

        # [[syrx_num1, date1], [syrx_num1, date2], ...]
        equipment_point_keys = []

        date = min_date
        while date <= max_date:
            if "min_date" not in equipment_point or "max_date" not in equipment_point \
                    or date < equipment_point["min_date"] or date > equipment_point["max_date"]:
                for p in parameter_points:
                    equipment_point_keys.append([p["syrx_num"], date])

            if len(equipment_point_keys) >= 200:
                records = self.uow.energy_records.get_equipment_point_records_by_syrx_date(equipment_point_keys)
                records_by_date = dict(
                    (k, dict((r["syrx_num"], r) for r in v))
                    for k, v in groupby(records, lambda xx: xx["date"]))
                self._evaluate_equipment_point_records(equipment_point, component_point, parameter_points,
                                                       records_by_date)
                equipment_point_keys = []

            date += datetime.timedelta(minutes=15)

        if len(equipment_point_keys) > 0:
            records = self.uow.energy_records.get_equipment_point_records_by_syrx_date(equipment_point_keys)
            records_by_date = dict(
                (k, dict((r["syrx_num"], r) for r in v))
                for k, v in groupby(records, lambda xx: xx["date"]))
            self._evaluate_equipment_point_records(equipment_point, component_point, parameter_points,
                                                   records_by_date)

        self.point_ranges.append({"syrx_num": equipment_point["syrx_num"],
                                  "start_date": min_date,
                                  "end_date": max_date})

    def _evaluate_equipment_point_records(self, equipment_point, component_point, parameter_points, records_by_date):
        equipment_point_records = []
        evaluator = Evaluator()
        for date, records_by_syrx_num in records_by_date.iteritems():
            if len(records_by_syrx_num) == 0:
                continue

            parameters = dict((p["point_code"].upper(), records_by_syrx_num[p["syrx_num"]]["value"])
                              for p in parameter_points if p['syrx_num'] in records_by_syrx_num)
            try:
                value = evaluator.evaluate(component_point["expression_tree"]["expression_tree"], parameters)
            except:
                print "Error evaluating syrx_num: " + equipment_point['syrx_num']
                continue

            syrx_num = equipment_point["syrx_num"]
            weather = records_by_syrx_num.values()[0]["weather"]
            created_on = pytz.UTC.localize(datetime.datetime.utcnow())

            equipment_point_record = self.uow.energy_records.get_equipment_point_record(date, syrx_num,
                                                                                        value, weather, created_on)

            equipment_point_records.append(equipment_point_record)

        self.uow.energy_records.insert_equipment_point_records(equipment_point_records)

    def _get_date_range_for_equipment_points(self, equipment_points):
        min_date = None
        max_date = None

        for equipment_point in equipment_points:
            # find a min date and max date for equipment point
            ep_dates = self.uow.energy_records.get_equipment_point_dates(equipment_point)
            if len(ep_dates) > 0:
                ep_min_date = min(ep_dates)
                ep_max_date = max(ep_dates)

                equipment_point['min_date'] = ep_min_date
                equipment_point['max_date'] = ep_max_date

                # update min/max dates accordingly
                if min_date and ep_min_date < min_date:
                    min_date = ep_min_date
                if max_date and ep_max_date > max_date:
                    max_date = ep_max_date
            else:
                equipment_point['min_date'] = None
                equipment_point['max_date'] = None

        if not min_date:
            min_date = datetime.datetime(2014, 1, 1, tzinfo=pytz.UTC)
        if not max_date:
            max_date = pytz.utc.localize(datetime.datetime.utcnow())

        return min_date, max_date

    def _get_points_for_component_id(self, component_id):
        if component_id not in self.points_by_component_id:
            points = self.uow.component_points.get_points_for_component_id(component_id)
            self.points_by_component_id[component_id] = points
        return self.points_by_component_id[component_id]

    def _is_point_safe(self, point_code, point_execution_stack=None):
        if point_code not in self.calculated_points_by_code:
            return False

        if point_execution_stack is None:
            point_execution_stack = []

        point = self.calculated_points_by_code[point_code]

        # test if the point threw an error
        if 'invalid' in point and point['invalid']:
            return False

        if point_code in point_execution_stack:
            return False
        elif len(point["dependencies"]) == 0:
            return True
        else:
            point_execution_stack = copy.copy(point_execution_stack)
            point_execution_stack.append(point_code)
            for dependency in point["dependencies"]:
                dependency_safe = self._is_point_safe(dependency, point_execution_stack)
                if not dependency_safe:
                    return False
            return True

    def _compile_equipment_point_records(self):
        compiler = EnergyRecordCompiler()
        for r in self.point_ranges:
            syrx_num = r["syrx_num"]
            start_date = r["start_date"]
            end_date = r["end_date"]
            self.uow.compiled_energy_records.delete_compiled_equipment_point_records(syrx_num, start_date, end_date)
            compiler.compile_component_point_records_by_year_span(syrx_num, start_date, end_date)


if __name__ == "__main__":
    calculated_point_handler = CalculatedPointHandler()
    calculated_point_handler.run()