import uuid
from db.uow import UoW
import rethinkdb
import xlrd
import re


class Importer:
    def __init__(self):
        self.uow = UoW(None)
        self.original_descriptions = dict()
        self.components_by_num = dict()
        self.file_path = None
        self.components_to_insert = dict()
        self.components_to_update = dict()

    """
    {
        "description":  "DATA COMMUNICATIONS" ,
        "id":  "00cddbda-7b59-4754-9272-73abe0d18359" ,
        "mapping_child_ids": [ ],
        "mapping_parent_ids": [ ],
        "mapping_root": false ,
        "num":  "27 24 29" ,
        "protected": true ,
        "structure_child_ids": [ ],
        "structure_parent_id":  "e6322a6f-ec78-4af1-b8f8-74db7bdf922f"
    }
    """

    @staticmethod
    def get_parent_component_num(num):
        current_num_position = len(num) - 1
        while current_num_position > 0:
            if num[current_num_position] == "." or num[current_num_position] == " ":
                parent_num = num[0:current_num_position]
                if len(parent_num) == 5:
                    parent_num = parent_num[0:4] + "0"
                return parent_num
            current_num_position -= 1
        return None

    def get_parent_for(self, num):
        parent_num = self.get_parent_component_num(num)
        try:
            parent_component = self.components_by_num[parent_num]
            return parent_component
        except:
            grandparent_component = self.get_parent_for(parent_num)
            if grandparent_component is None:
                return None

            parent_component = {
                "description":  grandparent_component["description"],
                "id": str(uuid.uuid4()),
                "mapping_child_ids": [],
                "mapping_parent_ids": [],
                "mapping_root": False,
                "num": str(num),
                "protected": False,
                "structure_child_ids": [],
                "structure_parent_id":  grandparent_component["id"]
            }

            grandparent_component["structure_child_ids"].append(parent_component["id"])
            if grandparent_component["num"] not in self.components_to_insert:
                self.components_to_update[grandparent_component["num"]] = grandparent_component

            self.components_to_insert[parent_component["num"]] = parent_component

            return parent_component


    def load_existing_components(self):
        components = self.uow.components.get_all()
        self.components_by_num = dict((c["num"], c) for c in components)
        self.original_descriptions = dict((c["num"], c["description"]) for c in components)

    def load_from_spreadsheet(self):
        wb = xlrd.open_workbook(self.file_path)
        sheet = wb.sheet_by_index(0)

        for row in range(1, sheet.nrows):
            num = sheet.cell(row, 0).value
            description = sheet.cell(row, 1).value

            if num in self.components_by_num:
                component = self.components_by_num[num]
                if component["description"] != description:
                    component["description"] = description
            else:
                component = {
                    "description":  description,
                    "id": str(uuid.uuid4()),
                    "mapping_child_ids": [],
                    "mapping_parent_ids": [],
                    "mapping_root": False,
                    "num":  str(num),
                    "protected": False,
                    "structure_child_ids": [],
                    "structure_parent_id":  None
                }

                try:
                    parent_component = self.get_parent_for(num)
                    component["structure_parent_id"] = parent_component["id"]
                    parent_component["structure_child_ids"].append(component["id"])
                    if parent_component["num"] not in self.components_to_insert:
                        self.components_to_update[parent_component["num"]] = parent_component
                except:
                    # no parent could be found, leave component["structure_parent_id"] as None
                    pass


                self.components_to_insert[num] = component
                self.components_by_num[num] = component

    def save_to_db(self):
        for component in self.components_by_num.values():
            if component["num"] in self.original_descriptions and \
                            component["description"] != self.original_descriptions[component["num"]]:
                self.components_to_update[component["num"]] = component


        batch_pointer = 0
        components_to_insert = self.components_to_insert.values()
        print(str(len(components_to_insert)) + " components to insert")
        while batch_pointer < len(components_to_insert):
            end_batch_pointer = batch_pointer + 200
            self.uow.components.insert_bulk(components_to_insert[batch_pointer:end_batch_pointer])
            batch_pointer = end_batch_pointer
            print(str(end_batch_pointer) + "/" + str(len(components_to_insert)) + " inserted")

        batch_pointer = 0
        components_to_update = self.components_to_update.values()
        print(str(len(components_to_update)) + " components to update")
        while batch_pointer < len(components_to_update):
            end_batch_pointer = batch_pointer + 1
            #self.uow.components.update_bulk(components_to_update[batch_pointer:end_batch_pointer])
            self.uow.components.update_raw(components_to_update[batch_pointer])
            batch_pointer = end_batch_pointer
            print(str(end_batch_pointer) + "/" + str(len(components_to_update)) + " updated")


if __name__ == "__main__":
    importer = Importer()
    importer.file_path = "/home/sean/Downloads/Master CLB Import Files forTiger 7,242,015.xlsx"
    importer.load_existing_components()
    importer.load_from_spreadsheet()
    importer.save_to_db()