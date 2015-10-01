import uuid
import pyodbc
from api.models.Component import Component
from db.uow import UoW
from function_parser import FunctionParser
import pytz
import datetime
import xlrd
from api.models.ComponentPoint import ComponentPoint
import logging


class MasterFormatImporter:

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename="master_format_importer.log", level=logging.INFO)

    def __init__(self):
        self.uow = UoW(None)
        self.conn = pyodbc.connect("DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=PathianDbNet;integrated security=True")
        self.components_by_num = {}

    def import_from_sqlserver(self):
        query = """
            SELECT d.Id DivisionId, d.Description DivisionDescription,
                s.Id SectionId, s.Description SectionDescription,
                t.Id TypeId, s.Description TypeDescription,
                c.Id ComponentId, c.Description ComponentDescription
            FROM EquipmentDivisions d
            LEFT JOIN EquipmentSections s on s.EquipmentDivisionId = d.Id
            LEFT JOIN EquipmentTypes t on t.EquipmentSectionId = s.Id
            LEFT JOIN EquipmentComponents c on c.EquipmentTypeId = t.Id
            ORDER BY d.Id, s.Id, t.Id, c.Id
        """
        cursor = self.conn.cursor()
        cursor.execute(query)

        num_inserted = 0
        components_to_insert = []

        current_division = None
        current_section = None
        current_type = None
        current_component = None

        for row in cursor:
            if current_division is not None and current_division["num"] != row.DivisionId:
                if len(components_to_insert) > 200:
                    # We wait until the division changes before inserting any records so that
                    # we know we don't have to add already-imported records as children to
                    # anything else

                    self.uow.components.insert_bulk(components_to_insert)

                    num_inserted += len(components_to_insert)
                    print("inserted " + str(num_inserted) + " components")
                    components_to_insert = []

                current_division = None

            if current_section is not None and (row.SectionId is None or current_section["num"] != row.SectionId):
                current_section = None

            if current_type is not None and (row.TypeId is None or current_type["num"] != row.TypeId):
                current_type = None

            if current_component is not None and (row.ComponentId is None or current_component["num"] != row.ComponentId):
                current_component = None

            if current_division is None:
                current_division = {"id": str(uuid.uuid4()), "num": row.DivisionId, "description": row.DivisionDescription,
                                    "structure_child_ids": [], "structure_parent_id": None, "mapping_root": False,
                                    "mapping_child_ids": [], "mapping_parent_ids": [],
                                    "protected": True}
                components_to_insert.append(current_division)

            if current_section is None and row.SectionId is not None:
                current_section = {"id": str(uuid.uuid4()), "num": row.SectionId, "description": row.SectionDescription,
                                   "structure_child_ids": [], "structure_parent_id": current_division["id"], "mapping_root": False,
                                    "mapping_child_ids": [], "mapping_parent_ids": [],
                                   "protected": True}
                components_to_insert.append(current_section)

            if current_type is None and row.TypeId is not None:
                current_type = {"id": str(uuid.uuid4()), "num": row.TypeId, "description": row.TypeDescription,
                                "structure_child_ids": [], "structure_parent_id": current_section["id"], "mapping_root": False,
                                "mapping_child_ids": [], "mapping_parent_ids": [],
                                "protected": True}
                components_to_insert.append(current_type)

            if current_component is None and row.ComponentId is not None:
                current_component = {"id": str(uuid.uuid4()), "num": row.ComponentId, "description": row.ComponentDescription,
                                     "structure_child_ids": [], "structure_parent_id": current_type["id"], "mapping_root": False,
                                     "mapping_child_ids": [], "mapping_parent_ids": [],
                                     "protected": True}
                components_to_insert.append(current_component)

            if current_section is not None and current_section["id"] not in current_division["structure_child_ids"]:
                current_division["structure_child_ids"].append(current_section["id"])

            if current_type is not None and current_type["id"] not in current_section["structure_child_ids"]:
                current_section["structure_child_ids"].append(current_type["id"])

            if current_component is not None and current_component["id"] not in current_type["structure_child_ids"]:
                current_type["structure_child_ids"].append(current_component["id"])

    def load_existing_components(self):
        components = self.uow.components.get_all()
        self.components_by_num = dict((c["num"], c) for c in components)

    def import_master_format_from_spreadsheet(self):
        wb = xlrd.open_workbook(self.file_path)
        equip_code_master_sheet = wb.sheet_by_index(0)

        last_level_two_component = None
        last_level_two_component_num = None
        last_level_two_component_id = None
        last_level_three_component = None
        last_level_three_component_num = None
        last_level_three_component_id = None

        for rowx in range(2, equip_code_master_sheet.nrows):
            level_two_component_num = equip_code_master_sheet.cell(rowx, 0).value

            # We will most likely only have a value for level_two_component_num if it has changed,
            # but here we check to see if we have a value and it's different than the previous value
            if level_two_component_num and (not last_level_two_component_num or last_level_two_component_num != level_two_component_num):
                last_level_three_component = None
                last_level_three_component_num = None
                last_level_three_component_id = None

                # try to pull it out of the database, if it fails then insert a new record
                try:
                    last_level_two_component = self.components_by_num[level_two_component_num]
                    if last_level_two_component["description"] != equip_code_master_sheet.cell(rowx, 1).value:
                        last_level_two_component["description"] = equip_code_master_sheet.cell(rowx, 1).value
                        last_level_two_component_obj = Component(last_level_two_component)
                        self.uow.components.update(last_level_two_component_obj)

                except KeyError:
                    code_split_by_space = level_two_component_num.split(" ")
                    parent_component_num = code_split_by_space[0]
                    try:
                        parent_component = self.components_by_num[parent_component_num]
                    except KeyError:
                        parent_component = {
                            "description": "NO DESCRIPTION AVAILABLE",
                            "mapping_root": False,
                            "num": parent_component_num,
                            "protected": False,
                            "structure_child_ids": [],
                            "structure_parent_id": None,
                            "mapping_child_ids": [],
                            "mapping_parent_ids": [],
                            "mapping_root": True
                        }
                        parent_component_obj = Component(parent_component)
                        self.uow.components.insert(parent_component_obj, no_parent_processing=True)
                        parent_component["id"] = parent_component_obj.id
                        self.components_by_num[parent_component["id"]] = parent_component

                    last_level_two_component = {
                        "description": equip_code_master_sheet.cell(rowx, 1).value,
                        "mapping_root": False,
                        "num": level_two_component_num,
                        "protected": False,
                        "structure_child_ids": [],
                        "structure_parent_id": parent_component["id"],
                        "mapping_child_ids": [],
                        "mapping_parent_ids": [],
                    }

                    last_level_two_component_obj = Component(last_level_two_component)
                    self.uow.components.insert(last_level_two_component_obj, no_parent_processing=True)
                    last_level_two_component["id"] = last_level_two_component_obj.id
                    self.components_by_num[last_level_two_component["id"]] = last_level_two_component

                    parent_component["structure_child_ids"].append(last_level_two_component["id"])
                    parent_component_obj = Component(parent_component)
                    self.uow.components.update(parent_component_obj)

                last_level_two_component_id = last_level_two_component["id"]
                last_level_two_component_num = level_two_component_num

            # We will most likely only have a value for level_two_component_num if it has changed,
            # but here we check to see if we have a value and it's different than the previous value
            level_three_component_num = equip_code_master_sheet.cell(rowx, 2).value
            if level_three_component_num and (not last_level_three_component_num or last_level_three_component_num != level_three_component_num):

                # try to pull it out of the database, if it fails then insert a new record
                try:
                    last_level_three_component = self.components_by_num[level_three_component_num]
                    if last_level_three_component["description"] != equip_code_master_sheet.cell(rowx, 3).value:
                        last_level_three_component["description"] = equip_code_master_sheet.cell(rowx, 3).value
                        last_level_three_component_obj = Component(last_level_three_component)
                        self.uow.components.update(last_level_three_component_obj)

                except KeyError:
                    last_level_three_component = {
                        "description": equip_code_master_sheet.cell(rowx, 3).value,
                        "mapping_root": False,
                        "num": level_three_component_num,
                        "protected": False,
                        "structure_child_ids": [],
                        "structure_parent_id": last_level_two_component_id,
                        "mapping_child_ids": [],
                        "mapping_parent_ids": [],
                    }

                    last_level_three_component_obj = Component(last_level_three_component)
                    self.uow.components.insert(last_level_three_component_obj, no_parent_processing=True)
                    last_level_three_component["id"] = last_level_three_component_obj.id
                    self.components_by_num[last_level_three_component["id"]] = last_level_three_component

                    last_level_two_component["structure_child_ids"].append(last_level_three_component["id"])
                    last_level_two_component_obj = Component(last_level_two_component)
                    self.uow.components.update(last_level_two_component_obj)

                last_level_three_component_id = last_level_three_component["id"]
                last_level_three_component_num = level_three_component_num

            # We will most likely only have a value for level_two_component_num if it has changed,
            # but here we check to see if we have a value and it's different than the previous value
            level_four_component_num = equip_code_master_sheet.cell(rowx, 4).value
            if level_four_component_num:

                # try to pull it out of the database, if it fails then insert a new record
                try:
                    last_level_four_component = self.components_by_num[level_four_component_num]
                    if last_level_four_component["description"] != equip_code_master_sheet.cell(rowx, 5).value:
                        last_level_four_component["description"] = equip_code_master_sheet.cell(rowx, 5).value
                        last_level_four_component_obj = Component(last_level_four_component)
                        self.uow.components.update(last_level_four_component_obj)

                except KeyError:
                    last_level_four_component = {
                        "description": equip_code_master_sheet.cell(rowx, 5).value,
                        "mapping_root": False,
                        "num": level_four_component_num,
                        "protected": False,
                        "structure_child_ids": [],
                        "structure_parent_id": last_level_three_component_id,
                        "mapping_child_ids": [],
                        "mapping_parent_ids": [],
                    }

                    last_level_four_component_obj = Component(last_level_four_component)
                    self.uow.components.insert(last_level_four_component_obj, no_parent_processing=True)
                    last_level_four_component["id"] = last_level_four_component_obj.id
                    self.components_by_num[last_level_four_component["id"]] = last_level_four_component

                    last_level_three_component["structure_child_ids"].append(last_level_four_component["id"])
                    last_level_three_component_obj = Component(last_level_three_component)
                    self.uow.components.update(last_level_three_component_obj)

    def load_units(self):
        wb = xlrd.open_workbook(self.file_path)
        sheet = wb.sheet_by_index(9)

        self.units = dict()
        for rowx in range(3, sheet.nrows):
            id = sheet.cell(rowx, 0).value
            units = sheet.cell(rowx, 1).value
            description = sheet.cell(rowx, 2).value
            self.units[id] = {"units": units, "description": description}

    def load_energy_point_types(self):
        wb = xlrd.open_workbook(self.file_path)
        sheet = wb.sheet_by_index(1)

        self.energy_point_types = dict()
        for rowx in range(3, sheet.nrows):
            id = sheet.cell(rowx, 0).value
            code = sheet.cell(rowx, 1).value
            description = sheet.cell(rowx, 2).value
            units_id = sheet.cell(rowx, 3).value
            self.energy_point_types[id] = {"code": code, "description": description, "units_id": units_id}

    def load_numeric_point_types(self):
        wb = xlrd.open_workbook(self.file_path)
        sheet = wb.sheet_by_name("Numeric Inputs ID Table")

        self.numeric_point_types = dict()
        for rowx in range(3, sheet.nrows):
            id = sheet.cell(rowx, 0).value
            code = sheet.cell(rowx, 1).value
            description = sheet.cell(rowx, 2).value
            units_id = sheet.cell(rowx, 3).value
            self.numeric_point_types[id] = {"code": code, "description": description, "units_id": units_id}

    def import_energy_points_from_spreadsheet(self):

        wb = xlrd.open_workbook(self.file_path)
        l3_points_sheet = wb.sheet_by_index(2)
        l4_points_sheet = wb.sheet_by_index(3)

        points_sheets = [l3_points_sheet, l4_points_sheet]

        for points_sheet in points_sheets:
            for rowx in range(4, points_sheet.nrows):
                component_num = points_sheet.cell(rowx, 0).value.strip()
                point_type_id = points_sheet.cell(rowx, 2).value
                code = points_sheet.cell(rowx, 3).value
                point_description = points_sheet.cell(rowx, 4).value

                try:
                    component = self.components_by_num[component_num]
                    component_point = ComponentPoint({
                        "component_num": component["num"],
                        "component_id": component["id"],
                        "point_type": "EP",
                        "description": point_description,
                        "code": code,
                        "units": self.units[self.energy_point_types[point_type_id]["units_id"]]["units"]})
                    self.uow.component_points.insert(component["id"], component_point)

                except KeyError:
                    logging.error("Could not find component for energy point " + component_point.code)

    def load_calculations(self):
        wb = xlrd.open_workbook(self.file_path)
        sheet = wb.sheet_by_name("Calculations ID Table")

        self.calculations = dict()

        current_calculation = {
            "id": None,
            "code": None,
            "description": None,
            "formula": None,
            "parameters": set(),
            "units": None
        }
        for row_num in range(3, sheet.nrows + 1):
            if row_num < sheet.nrows:
                id = sheet.cell(row_num, 1).value
                code = sheet.cell(row_num, 2).value
                description = sheet.cell(row_num, 3).value
                formula = sheet.cell(row_num, 4).value
                energy_point_code = sheet.cell(row_num, 6).value
                numeric_point_code = sheet.cell(row_num, 8).value
                calculated_point_code = sheet.cell(row_num, 10).value
                units = sheet.cell(row_num, 12).value
            else:
                code = None

            if (code or row_num == sheet.nrows) and (current_calculation["code"] is None or code != current_calculation["code"]):
                if current_calculation["code"]:
                    expression_tree = None
                    try:
                        expression_tree = FunctionParser.parse(current_calculation["formula"])

                        identifier_names = set(expression_tree["identifier_names"])
                        if len(current_calculation["parameters"] - identifier_names) > 0:
                            logging.info("Unknown parameters in formula for calculation " + current_calculation["code"])

                        current_calculation["parameters"] = identifier_names

                        self.calculations[current_calculation["id"]] = current_calculation

                    except Exception as e:
                        logging.error("Error parsing formula for calculation " + current_calculation["code"])

                current_calculation = {
                    "id": id,
                    "code": code,
                    "description": description,
                    "formula": formula.split("=")[1],
                    "parameters": set(),
                    "units": units
                }


            if energy_point_code:
                current_calculation["parameters"].add(energy_point_code.upper())
            if numeric_point_code:
                current_calculation["parameters"].add(numeric_point_code.upper())
            if calculated_point_code:
                current_calculation["parameters"].add(calculated_point_code.upper())

        logging.info("Found " + str(len(self.calculations)) + " calculations")

    def import_calculated_points_from_spreadsheet(self):

        wb = xlrd.open_workbook(self.file_path)
        l3_points_sheet = wb.sheet_by_name("MF Calc Points Table L3")
        l4_points_sheet = wb.sheet_by_name("MF Calc Points Table L4")

        points_sheets = [l3_points_sheet, l4_points_sheet]

        for points_sheet in points_sheets:
            for row_num in range(3, points_sheet.nrows):
                component_num = points_sheet.cell(row_num, 0).value.strip()
                calculation_id = points_sheet.cell(row_num, 2).value
                code = points_sheet.cell(row_num, 3).value
                point_description = points_sheet.cell(row_num, 4).value

                try:
                    component = self.components_by_num[component_num]
                    calculation = self.calculations[calculation_id]
                    component_point = ComponentPoint({
                        "component_num": component["num"],
                        "component_id": component["id"],
                        "point_type": "CP",
                        "description": point_description,
                        "code": code,
                        "formula": calculation["formula"],
                        "units": calculation["units"],
                        "parameters": [{"name": p, "point_id": None} for p in calculation["parameters"]]
                    })
                    self.uow.component_points.insert(component["id"], component_point)

                except KeyError:
                    logging.error("Could not find component for calculated point " + component_point.code)

    def import_position_points_from_spreadsheet(self):

        wb = xlrd.open_workbook(self.file_path)
        points_sheet = wb.sheet_by_name("MF Pos Points L3")

        for row_num in range(4, points_sheet.nrows):
            component_num = points_sheet.cell(row_num, 0).value.strip()
            code = points_sheet.cell(row_num, 3).value
            point_description = points_sheet.cell(row_num, 4).value

            try:
                component = self.components_by_num[component_num]
                component_point = ComponentPoint({
                    "component_num": component["num"],
                    "component_id": component["id"],
                    "point_type": "PP",
                    "description": point_description,
                    "code": code
                })
                self.uow.component_points.insert(component["id"], component_point)

            except KeyError:
                logging.error("Could not find component for position point " + component_point.code)

    def import_numeric_points_from_spreadsheet(self):

        wb = xlrd.open_workbook(self.file_path)
        l3_points_sheet = wb.sheet_by_name("MF Numeric Inputs Table L3")
        l4_points_sheet = wb.sheet_by_name("MF Numeric Inputs Table L4")

        points_sheets = [l3_points_sheet, l4_points_sheet]

        for points_sheet in points_sheets:
            for row_num in range(3, points_sheet.nrows):
                component_num = points_sheet.cell(row_num, 0).value.strip()
                point_type_id = points_sheet.cell(row_num, 2).value
                code = points_sheet.cell(row_num, 3).value
                point_description = points_sheet.cell(row_num, 4).value

                try:
                    component = self.components_by_num[component_num]
                    component_point = ComponentPoint({
                        "component_num": component["num"],
                        "component_id": component["id"],
                        "point_type": "NP",
                        "description": point_description,
                        "code": code,
                        "units": self.units[self.numeric_point_types[point_type_id]["units_id"]]["units"]
                    })
                    self.uow.component_points.insert(component["id"], component_point)

                except KeyError:
                    logging.error("Could not find component for numeric point " + component_point.code)

if __name__ == "__main__":
    importer = MasterFormatImporter()
    importer.file_path = "c:\\Users\\sprice\\Documents\\Work\\Pathian\\Syrx tables\\MF Energy Point Tables - Master Copy Rev 6 03282014.xlsx"

    importer.import_from_sqlserver()
    importer.load_existing_components()
    importer.load_units()
    importer.load_energy_point_types()
    importer.load_calculations()
    importer.load_numeric_point_types()
    importer.import_master_format_from_spreadsheet()
    importer.import_energy_points_from_spreadsheet()
    importer.import_calculated_points_from_spreadsheet()
    importer.import_position_points_from_spreadsheet()
    importer.import_numeric_points_from_spreadsheet()