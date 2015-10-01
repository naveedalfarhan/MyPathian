from datetime import datetime, timedelta
from api.models.Equipment import Equipment
from api.models.Paragraph import Paragraph
from api.models.QueryParameters import QueryResult
import pytz
import rethinkdb as r


class EquipmentRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.equipment
        self.components_table = uow.tables.components
        self.component_points_table = uow.tables.component_points
        self.component_issues_table = uow.tables.component_issues
        self.component_tasks_table = uow.tables.component_tasks
        self.equipment_issues_table = uow.tables.equipment_issues
        self.equipment_tasks_table = uow.tables.equipment_tasks
        self.equipment_paragraphs_table = uow.tables.equipment_paragraphs
        self.equipment_points_table = uow.tables.equipment_points
        self.equipment_raf_table = uow.tables.equipment_raf
        self.equipment_reset_schedule_table = uow.tables.equipment_reset_schedule
        self.groups_table = uow.tables.groups
        self.paragraph_definitions_table = uow.tables.paragraph_definitions
        self.syrx_categories_table = uow.tables.syrx_categories
        self.issues_table = uow.tables.issues
        self.tasks_table = uow.tables.tasks

    #
    # Equipment
    #

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get_equipment_points_by_equipment_id(self, query_parameters, equipment_id):
        q = self.equipment_points_table.get_all(equipment_id, index="equipment_id")
        q = q.order_by("syrx_num")
        if query_parameters is None:
            data = self.uow.run_list(q)
            return data
        cursor = self.uow.run(q.skip(query_parameters.skip).limit(query_parameters.take))

        data = list(cursor)
        total = self.uow.run(q.count())

        query_result = QueryResult(data, total)
        return query_result

    def get_next_highest_ascii_string(self, string):
        ascii_codes = [ord(c) for c in string]
        current_pointer = len(ascii_codes) - 1

        while True:
            if current_pointer < 0:
                return None

            ascii_codes[current_pointer] += 1
            if ascii_codes[current_pointer] == 256:
                ascii_codes[current_pointer] = 0
                current_pointer -= 1
            else:
                break

        chars = [chr(c) for c in ascii_codes]
        new_string = "".join(chars)
        return new_string

    def get_all_equipment_points_query_result(self, query_parameters):
        q = self.uow.tables.equipment_points

        if query_parameters is None:
            q = q.order_by("syrx_num")
            data = self.uow.run_list(q)
        else:
            if query_parameters.filter is not None and len(query_parameters.filter["filters"]) > 0:
                filter = query_parameters.filter["filters"][0]
                if filter["operator"] == "eq" and filter["field"] == "syrx_num":
                    q = q.between(filter["value"], filter["value"], index="syrx_num", right_bound="closed")
                elif filter["operator"] == "startswith" and filter["field"] == "syrx_num":
                    right_bound = self.get_next_highest_ascii_string(filter["value"])
                    q = q.between(filter["value"], right_bound, index="syrx_num")

            q = q.order_by(index="syrx_num")
            data = self.uow.run_list(q.skip(query_parameters.skip).limit(query_parameters.take))

        total = self.uow.run(q.count())
        return QueryResult(data, total)

    def get_all_vendor_points_query_result(self, query_parameters):
        q = self.uow.tables.vendor_points

        if query_parameters is None:
            q = q.order_by(index="vendor_sensor_id")
            data = self.uow.run_list(q)
        else:
            if query_parameters.filter is not None and len(query_parameters.filter["filters"]) > 0:
                vendor_filter = None
                sensor_id_filter = None

                if query_parameters.filter["filters"][0]["field"] == "vendor":
                    vendor_filter = query_parameters.filter["filters"][0]
                elif query_parameters.filter["filters"][0]["field"] == "sensor_id":
                    sensor_id_filter = query_parameters.filter["filters"][0]

                if len(query_parameters.filter["filters"]) > 1 and query_parameters.filter["filters"][1]["field"] == "vendor":
                    vendor_filter = query_parameters.filter["filters"][1]
                elif len(query_parameters.filter["filters"]) > 1 and query_parameters.filter["filters"][1]["field"] == "sensor_id":
                    sensor_id_filter = query_parameters.filter["filters"][1]

                if vendor_filter is not None and sensor_id_filter is None:

                    left_bound = [vendor_filter["value"], r.minval]
                    right_bound = [vendor_filter["value"], r.maxval]
                    q = q.between(left_bound, right_bound, index="vendor_sensor_id", right_bound="closed")
                    q = q.order_by(index="vendor_sensor_id")

                elif sensor_id_filter is not None and vendor_filter is None:

                    if sensor_id_filter["operator"] == "eq":
                        left_bound = sensor_id_filter["value"]
                        right_bound = sensor_id_filter["value"]
                        q = q.between(left_bound, right_bound, index="sensor_id", right_bound="closed")
                        q = q.order_by(index="sensor_id")

                    elif sensor_id_filter["operator"] == "startswith":
                        left_bound = sensor_id_filter["value"]
                        right_bound = self.get_next_highest_ascii_string(sensor_id_filter["value"])
                        q = q.between(left_bound, right_bound, index="sensor_id")
                        q = q.order_by(index="sensor_id")

                elif vendor_filter is not None and sensor_id_filter is not None:

                    if sensor_id_filter["operator"] == "eq":

                        left_bound = [vendor_filter["value"], sensor_id_filter["value"]]
                        right_bound = [vendor_filter["value"], sensor_id_filter["value"]]
                        q = q.between(left_bound, right_bound, index="vendor_sensor_id", right_bound="closed")
                        q = q.order_by(index="vendor_sensor_id")

                    elif sensor_id_filter["operator"] == "startswith":

                        left_bound = [vendor_filter["value"], sensor_id_filter["value"]]
                        right_bound = [vendor_filter["value"], self.get_next_highest_ascii_string(sensor_id_filter["value"])]
                        q = q.between(left_bound, right_bound, index="vendor_sensor_id")
                        q = q.order_by(index="vendor_sensor_id")

            else:
                q = q.order_by(index="vendor_sensor_id")

            data = self.uow.run_list(q.skip(query_parameters.skip).limit(query_parameters.take))

        total = self.uow.run(q.count())
        return QueryResult(data, total)

    def get_all_equipment_point_records_query_result(self, syrx_nums, start_date_epoch_time, end_date_epoch_time, query_parameters):

        start_date = datetime.fromtimestamp(start_date_epoch_time, tz=pytz.UTC)
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, 0, pytz.UTC)
        end_date = datetime.fromtimestamp(end_date_epoch_time, tz=pytz.UTC)
        end_date = datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0, 0, pytz.UTC) + timedelta(days=1)

        q = None


        for syrx_num in syrx_nums:
            sub_q = (self.uow.tables.equipment_point_records
                     .between([syrx_num, start_date],
                              [syrx_num, end_date],
                              index="syrx_num_date")
                     .order_by(index="syrx_num_date"))

            if q is None:
                q = sub_q
            else:
                q = q.union(sub_q)

        if query_parameters is None:
            data = self.uow.run_list(q.skip(0).limit(100))
        else:
            data = self.uow.run_list(q.skip(query_parameters.skip).limit(query_parameters.take))

        total = self.uow.run(q.count())
        return QueryResult(data, total)

    def get_all_vendor_records_query_result(self, points, start_date_epoch_time, end_date_epoch_time, query_parameters):

        start_date = datetime.fromtimestamp(start_date_epoch_time, tz=pytz.UTC)
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, 0, pytz.UTC)
        end_date = datetime.fromtimestamp(end_date_epoch_time, tz=pytz.UTC)
        end_date = datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0, 0, pytz.UTC) + timedelta(days=1)

        q = None

        for point in points:
            sub_q = (self.uow.tables.vendor_records
                     .between([point["vendor"], point["sensor_id"], start_date],
                              [point["vendor"], point["sensor_id"], end_date],
                              index="vendor_sensor_id_utc_timestamp")
                     .order_by(index="vendor_sensor_id_utc_timestamp"))

            if q is None:
                q = sub_q
            else:
                q = q.union(sub_q)

        if query_parameters is None:
            data = self.uow.run_list(q.skip(0).limit(100))
        else:
            data = self.uow.run_list(q.skip(query_parameters.skip).limit(query_parameters.take))

        total = self.uow.run(q.count())
        return QueryResult(data, total)


    def get_all_by_group(self, group_id, query_parameters=None):
        if query_parameters is None:
            return self.uow.run_list(self.table.get_all(group_id, index="group_id"))
        else:
            return self.uow.apply_query_parameters(self.table.filter({"group_id": group_id}), query_parameters)

    def get_equipment_for_group(self, group_id):
        return self.uow.run_list(self.table.get_all(group_id, index="group_id"))

    def get_by_id(self, model_id):
        model_raw = list(self.uow.run(self.table.get_all(model_id)
                                 .eq_join("group_id", self.groups_table)
                                 .map(lambda(x): {"left": x["left"], "right": {"group": x["right"]}})
                                 .zip()
                                 .eq_join("component_id", self.components_table)
                                 .map(lambda(x): {"left": x["left"],
                                                  "right": {"component": {"id": x["right"]["id"],
                                                                          "name": x["right"]["num"] + " "
                                                                                  + x["right"]["description"]}}})
                                 .zip()))[0]

        if model_raw is None:
            return None

        model = Equipment(model_raw)

        if len(model.subcomponent_ids) == 0:
            model.subcomponents = []
        else:
            model.subcomponents = self.uow.run_list(self.components_table
                                                    .get_all(*model.subcomponent_ids)
                                                    .map(lambda(x): {"id": x["id"],
                                                                     "name": x["num"] + " " + x["description"]}))

        points = self.uow.run_list(self.equipment_points_table
                                         .get_all(model_id, index="equipment_id")
                                         .map(lambda(x): {"id": x["component_point_id"],
                                                          'syrx_num': x['syrx_num']}))

        model.syrx_nums = sorted([p['syrx_num'] for p in points])
        model.points = [{'id': p['id']} for p in points]

        model.paragraphs = self.uow.run_list(self.equipment_paragraphs_table
                                             .get_all(model_id, index="equipment_id")
                                             .map(lambda(x): {"id": x["paragraph_id"]}))
        return model

    def insert_equipment_points(self, equipment, group, point_ids):
        #find points to map
        if len(point_ids) == 0:
            points = []
        else:
            points = self.uow.run(self.component_points_table.get_all(*point_ids))
        points_by_id = dict((point["id"], point) for point in points)

        #convert to equipment points
        equipment_points = []
        for point_id in point_ids:
            point = points_by_id[point_id]
            point_num = point["component_point_num"]
            equipment_point = {
                "equipment_id": equipment.id,
                "component_point_id": point_id,
                "syrx_num": str(group["num"]) + "-" + equipment.num + "-" + point_num,
                "id": str(group["num"]) + "-" + equipment.num + "-" + point_num,
                "component_point_num": point["component_point_num"],
                "component_id": point["component_id"],
                "point_code": point["code"],
                "point_type": point["point_type"],
                "point_description": point["description"]
            }
            if 'units' in point:
                equipment_point['units'] = point['units']
                
            equipment_points.append(equipment_point)

        if len(equipment_points) > 0:
            self.uow.run(self.equipment_points_table.insert(equipment_points))

    def insert(self, group_id, model):
        #ensure there is no id
        try:
            del model.id
        except AttributeError:
            pass

        group = self.uow.run(self.groups_table.get(group_id))

        #get the next equipment number in sequence for generating syrx numbers
        if "next_equipment_num" not in group:
            model.num = "1"
            group["next_equipment_num"] = "2"
        else:
            model.num = group["next_equipment_num"]
            group["next_equipment_num"] = str(int(group["next_equipment_num"]) + 1)

        #save the modified next number
        self.uow.run(self.groups_table.get(group_id).update(group))

        #pluck the point and paragraph from the model
        point_ids = [point["id"] for point in model.points]
        paragraph_ids = [paragraph["id"] for paragraph in model.paragraphs]

        #clean the model
        del model.points
        del model.paragraphs

        #insert the equipment model to generate the ids
        ret = self.uow.run(self.table.insert(model.__dict__))
        equipment_id = ret["generated_keys"][0]
        model.id = equipment_id

        self.insert_equipment_points(model, group, point_ids)

        if paragraph_ids and len(paragraph_ids) > 0:
            #get the paragraphs to copy over
            paragraphs = self.uow.run(
                self.paragraph_definitions_table.get_all(*paragraph_ids)
                    .eq_join('category_id', self.syrx_categories_table)
                    .without({'right': {'id': True}})
                    .zip()
                    .map(lambda p: p.merge({'category_name': p['name']}))
                    .without('name')
            )
        else:
            paragraphs = []

        #convert to equipment_paragraphs
        equipment_paragraphs = []
        paragraph_sort_orders = self.build_empty_sort_orders()
        for paragraph in paragraphs:
            current_type = paragraph["type"]
            current_component = paragraph["component_id"]
            current_category = paragraph["category_name"]
            if not current_component in paragraph_sort_orders[current_type]:  # component level missing
                paragraph_sort_orders[current_type][current_component] = {}
                paragraph_sort_orders[current_type][current_component][current_category] = 1
            else:  # component exists
                if not current_category in paragraph_sort_orders[current_type][current_component]:  # category missing
                    paragraph_sort_orders[current_type][current_component][current_category] = 1

            equipment_paragraph = {
                "equipment_id": equipment_id,
                "paragraph_id": paragraph["id"],
                "component_id": paragraph["component_id"],
                "num": str(group["num"]) + "-" + model.num + "-" + paragraph["num"],
                "description": paragraph["description"],
                "type": current_type,
                "title": paragraph["title"],
                "category_id": paragraph["category_id"],
                "sort_order": paragraph_sort_orders[current_type][current_component][current_category]
            }
            equipment_paragraphs.append(equipment_paragraph)
            paragraph_sort_orders[current_type][current_component][current_category] += 1

        self.uow.run(self.equipment_paragraphs_table.insert(equipment_paragraphs))

    def update(self, model):
        group = self.uow.run(self.groups_table.get(model.group_id))

        existing_equipment_points = self.uow.run_list(self.equipment_points_table.get_all(model.id, index="equipment_id"))
        existing_equipment_points_by_component_point_id = dict((p["component_point_id"], p) for p in existing_equipment_points)

        model_point_ids = [point["id"] for point in model.points]

        point_ids_to_add = [p_id for p_id in model_point_ids if p_id not in existing_equipment_points_by_component_point_id]

        if len(point_ids_to_add) > 0:
            self.insert_equipment_points(model, group, point_ids_to_add)

        point_ids_to_remove = [p_id for p_id in existing_equipment_points_by_component_point_id if p_id not in model_point_ids]
        if len(point_ids_to_remove) > 0:
            self.uow.run(self.equipment_points_table.get_all(*point_ids_to_remove, index="component_point_id").delete())

        if len(model.paragraphs) > 0:
            #get ids of paragraphs from the submitted model
            paragraph_ids = [paragraph["id"] for paragraph in model.paragraphs]

            #fetch the paragraphs that we want to keep
            if len(paragraph_ids) > 0:
                paragraphs = self.uow.run_list(
                    self.equipment_paragraphs_table
                    .get_all(*paragraph_ids, index="paragraph_id")
                    .filter({'equipment_id': model.id})
                    .eq_join('category_id', self.syrx_categories_table)
                    .without({'right': {'id': True}})
                    .zip()
                    .map(lambda p: p.merge({'category_name': p['name']}))
                    .without('name')
                )
            else:
                paragraphs = []
            existing_paragraph_ids = [paragraph["paragraph_id"] for paragraph in paragraphs]

            #find the paragraphs that we want to add to the existing list
            paragraph_ids_to_add = list(set(paragraph_ids) - set(existing_paragraph_ids))
            if len(paragraph_ids_to_add) > 0:
                paragraphs_to_add = self.uow.run_list(
                    self.paragraph_definitions_table.get_all(*paragraph_ids_to_add)
                    .eq_join('category_id', self.syrx_categories_table)
                    .without({'right': {'id': True}})
                    .zip()
                    .map(lambda p: p.merge({'category_name': p['name']}))
                    .without('name')
                )
            else:
                paragraphs_to_add = []

            #combine the lists
            paragraphs.extend(paragraphs_to_add)

            #clear the existing paragraph mappings from the database
            self.uow.run(self.equipment_paragraphs_table.get_all(model.id, index="equipment_id").delete())

            #convert to equipment paragraphs
            equipment_paragraphs = []
            paragraph_sort_orders = self.build_initial_sort_orders(paragraphs)
            for paragraph in paragraphs:
                current_type = paragraph["type"]
                current_component = paragraph["component_id"]
                current_category = paragraph["category_name"]

                if not current_component in paragraph_sort_orders[current_type]:
                    paragraph_sort_orders[current_type][current_component] = {}

                if not current_category in paragraph_sort_orders[current_type][current_component]:
                    paragraph_sort_orders[current_type][current_component][current_category] = 1

                #paragraph definitions do not have 'paragraph_id' so we add it as a preemptive measure
                if not "paragraph_id" in paragraph:
                    paragraph["paragraph_id"] = paragraph["id"]

                if not "sort_order" in paragraph:
                    paragraph["sort_order"] = paragraph_sort_orders[current_type][current_component][current_category]
                    paragraph_sort_orders[current_type][current_component][current_category] += 1

                equipment_paragraph = {
                    "equipment_id": model.id,
                    "paragraph_id": paragraph["paragraph_id"],
                    "component_id": paragraph["component_id"],
                    "num": str(group["num"]) + "-" + model.num + "-" + str(paragraph["num"]),
                    "description": paragraph["description"],
                    "type": current_type,
                    "title": paragraph["title"],
                    "category_id": paragraph["category_id"],
                    "sort_order": paragraph["sort_order"]
                }
                equipment_paragraphs.append(equipment_paragraph)

            self.uow.run(self.equipment_paragraphs_table.insert(equipment_paragraphs))

        #clean up and save the model
        del model.points
        del model.paragraphs
        self.uow.run(self.table.update(model.__dict__))

    def delete(self, model_id):
        self.uow.run(self.equipment_points_table.get_all(model_id, index="equipment_id").delete())
        self.uow.run(self.equipment_paragraphs_table.get_all(model_id, index="equipment_id").delete())
        self.uow.run(self.table.get(model_id).delete())

    #
    # Equipment Points
    #

    def get_equipment_point_by_syrx_num(self, syrx_num):
        try:
            point = self.uow.run_list(self.equipment_points_table.get_all(syrx_num, index="syrx_num"))[0]
            return point
        except:
            return None


    def get_equipment_points_by_component_point_id(self, point_num):
        points = self.uow.run_list(self.equipment_points_table.get_all(point_num, index="component_point_id"))
        return points

    def get_equipment_points_by_component_point_ids(self, point_nums):
        points = self.uow.run_list(self.equipment_points_table.get_all(*point_nums, index="component_point_id"))
        return points

    def get_equipment_points_by_equipment_id_component_id(self, equipment_id, component_id):
        index_entry = [equipment_id, component_id]
        points = self.uow.run_list(self.equipment_points_table.get_all(index_entry, index="equipment_id_component_id"))
        return points

    #
    # Equipment Paragraphs
    #

    def get_all_paragraphs_for_equipment(self, equipment_id, paragraph_type=None):
        q = self.equipment_paragraphs_table.get_all(equipment_id, index="equipment_id")
        if paragraph_type is not None:
            q = q.filter({"type": paragraph_type})

        q = (q.eq_join("category_id", self.syrx_categories_table)
             .without({'right': ['id']})
             .zip()
             .eq_join("component_id", self.components_table)
             .map(lambda p: p.merge({'right': {'component_num': p['right']['num'],
                                               'component_description': p['right']['description']}}))
             .without({
                 'right': [
                     'id',
                     'description',
                     'mapping_root',
                     'mapping_child_ids',
                     'mapping_parent_ids',
                     'num',
                     'protected',
                     'structure_child_ids',
                     'structure_parent_id',
                     'next_AR',
                     'next_CI',
                     'next_CR',
                     'next_CS',
                     'next_CT',
                     'next_FT',
                     'next_DR',
                     'next_EP',
                     'next_LC',
                     'next_MR',
                     'next_PR',
                     'next_RR'
                 ]
             })
             .zip()
             .map(lambda p: p.merge({
                 'category_name': p['name'],
                 'component_full_name': p['component_num'] + ' - ' + p['component_description']
             }))
             .without(['name'])
             .order_by("component_full_name, category_name", "sort_order"))

        return self.uow.run(q)

    def get_paragraph_for_equipment(self, paragraph_id):
        paragraph = self.uow.run(self.equipment_paragraphs_table.get(paragraph_id))
        return Paragraph(paragraph)

    def move_paragraph_up(self, equipment_id, paragraph_id):
        paragraph = self.uow.run(self.equipment_paragraphs_table.get(paragraph_id))
        current_sort_order = paragraph["sort_order"]
        current_type = paragraph["type"]
        current_component = paragraph["component_id"]
        current_category_id = paragraph["category_id"]

        if current_sort_order is 1:
            return

        #get the next paragraph ahead of the current one (returns a cursor)
        paragraph_list = list(self.uow.run(
            self.equipment_paragraphs_table
            .filter({"equipment_id": equipment_id,
                     "type": current_type,
                     "component_id": current_component,
                     "category_id": current_category_id,
                     "sort_order": (current_sort_order - 1)})))

        #update higher paragraph in sort order if one is found
        if len(paragraph_list) > 0:
            next_paragraph = paragraph_list[0]
            next_paragraph["sort_order"] = current_sort_order
            self.uow.run(self.equipment_paragraphs_table.update(next_paragraph))

        #update current paragraph
        paragraph["sort_order"] = current_sort_order - 1
        self.uow.run(self.equipment_paragraphs_table.update(paragraph))

    def move_paragraph_down(self, equipment_id, paragraph_id):
        paragraph = self.uow.run(self.equipment_paragraphs_table.get(paragraph_id))
        current_sort_order = paragraph["sort_order"]
        current_type = paragraph["type"]
        current_component = paragraph["component_id"]
        current_category_id = paragraph["category_id"]

        #get the next paragraph ahead of the current one (returns a cursor)
        paragraph_list = list(self.uow.run(
            self.equipment_paragraphs_table
            .filter({"equipment_id": equipment_id,
                     "type": current_type,
                     "component_id": current_component,
                     "category_id": current_category_id,
                     "sort_order": (current_sort_order + 1)})))

        #update higher paragraph in sort order if one is found
        if len(paragraph_list) > 0:
            next_paragraph = paragraph_list[0]
            next_paragraph["sort_order"] = current_sort_order
            self.uow.run(self.equipment_paragraphs_table.update(next_paragraph))

            #update current paragraph if there was a lower ordered item
            paragraph["sort_order"] = current_sort_order + 1
            self.uow.run(self.equipment_paragraphs_table.update(paragraph))

    def delete_paragraph(self, equipment_id, paragraph_id):
        paragraph = self.uow.run(self.equipment_paragraphs_table.get(paragraph_id))
        self.uow.run(self.equipment_paragraphs_table.get(paragraph_id).delete())
        self.rebuild_sort_order(equipment_id, paragraph["type"], paragraph["component_id"], paragraph["category_id"])

    def rebuild_sort_order(self, equipment_id, paragraph_type, paragraph_component, paragraph_category):
        paragraphs = self.uow.run_list(self.equipment_paragraphs_table
            .filter({
                "equipment_id": equipment_id,
                "type": paragraph_type,
                "component_id": paragraph_component,
                "category_id": paragraph_category
            }).order_by('sort_order'))

        sort_order = 1
        for paragraph in paragraphs:
            paragraph["sort_order"] = sort_order
            sort_order += 1
            self.uow.run(self.equipment_paragraphs_table.update(paragraph))

    def insert_paragraph(self, model):
        del model.id
        result = self.uow.run(self.equipment_paragraphs_table.insert(model.__dict__))
        paragraph_id = result["generated_keys"][0]
        return paragraph_id

    def update_paragraph(self, model):
        self.uow.run(self.equipment_paragraphs_table.update(model.__dict__))

    def add_paragraph(self, equipment_id, paragraph_id):
        paragraph = self.uow.run(self.paragraph_definitions_table.get(paragraph_id))
        equipment = self.uow.run(self.table.get(equipment_id))
        group = self.uow.run(self.groups_table.get(equipment["group_id"]))
        component = self.uow.run(self.components_table.get(equipment["component_id"]))

        paragraph_exists_in_section = not self.uow.run(self.equipment_paragraphs_table
            .filter({
                "type": paragraph["type"],
                "component_id": component["id"],
                "category_id": paragraph["category_id"]
            }).is_empty())

        next_sort_order = 1

        if paragraph_exists_in_section:
            next_sort_order = self.uow.run(self.equipment_paragraphs_table
                .filter({
                    "type": paragraph["type"],
                    "component_id": component["id"],
                    "category_id": paragraph["category_id"]
                })
                .max("sort_order")
            )["sort_order"]

            next_sort_order += 1

        equipment_paragraph = {
            "equipment_id": equipment_id,
            "paragraph_id": paragraph["id"],
            "component_id": paragraph["component_id"],
            "num": str(group["num"]) + "-" + equipment["num"] + "-" + paragraph["num"],
            "description": paragraph["description"],
            "type": paragraph["type"],
            "title": paragraph["title"],
            "category_id": paragraph["category_id"],
            "sort_order": next_sort_order
        }

        self.uow.run(self.equipment_paragraphs_table.insert(equipment_paragraph))


    #
    # RAF Pressures
    #

    def get_raf(self, equipment_id):
        return self.uow.run_list(self.equipment_raf_table.get_all(equipment_id, index="equipment_id"))

    def insert_raf(self, raf):
        del raf.id
        result = self.uow.run(self.equipment_raf_table.insert(raf.__dict__))
        raf_id = result["generated_keys"][0]
        return raf_id

    def delete_raf(self, raf_id):
        self.uow.run(self.equipment_raf_table.get(raf_id).delete())

    #
    # Reset Schedules
    #

    def add_reset_schedule(self, equipment_id, reset_schedule_id):
        self.uow.run(self.equipment_reset_schedule_table.insert({"equipment_id": equipment_id, "reset_schedule_id": reset_schedule_id}))

    def get_reset_schedules(self, equipment_id):
        return self.uow.run_list(self.equipment_reset_schedule_table.get_all(equipment_id, index="equipment_id").map(lambda p: p["reset_schedule_id"]))

    def delete_reset_schedule(self, equipment_id, reset_schedule_id):
        self.uow.run(self.equipment_reset_schedule_table.filter({"equipment_id": equipment_id, "reset_schedule_id": reset_schedule_id}).delete())

    #
    # Equipment Issues
    #

    def get_equipment_issues(self, equipment_id):
        q = self.uow.run(self.equipment_issues_table.get_all(equipment_id, index="equipment_id"))

        issues = list(q)

        return issues

    def insert_equipment_issue(self, equipment_issue):
        del equipment_issue.id
        result = self.uow.run(self.equipment_issues_table.insert(equipment_issue.__dict__))
        equipment_issue_id = result["generated_keys"][0]
        return equipment_issue_id

    def update_equipment_issue(self, equipment_issue):
        self.uow.run(self.equipment_issues_table.update(equipment_issue.__dict__))

    def delete_equipment_issue(self, equipment_issue_id):
        self.uow.run(self.equipment_issues_table.get(equipment_issue_id).delete())

    #
    # Equipment Tasks
    #

    def get_equipment_tasks(self, equipment_id):
        q = self.uow.run(self.equipment_tasks_table.get_all(equipment_id, index="equipment_id"))

        tasks = list(q)

        return tasks

    def insert_equipment_task(self, equipment_task):
        del equipment_task.id
        result = self.uow.run(self.equipment_tasks_table.insert(equipment_task.__dict__))
        equipment_task_id = result["generated_keys"][0]
        return equipment_task_id

    def update_equipment_task(self, equipment_task):
        self.uow.run(self.equipment_tasks_table.update(equipment_task.__dict__))

    def delete_equipment_task(self, equipment_task_id):
        self.uow.run(self.equipment_tasks_table.get(equipment_task_id).delete())

    #
    # UTILITY FUNCTIONS
    #

    def build_empty_sort_orders(self):
        return {
            "AR": {},
            "CR": {},
            "CS": {},
            "DR": {},
            "FT": {},
            "LC": {},
            "MR": {},
            "PR": {},
            "RR": {}
        }

    def build_initial_sort_orders(self, paragraphs):
        types = list(set([paragraph["type"] for paragraph in paragraphs]))
        components = list(set([paragraph["component_id"] for paragraph in paragraphs]))
        categories = list(set([paragraph["category_name"] for paragraph in paragraphs]))

        paragraph_sorts = self.build_empty_sort_orders()

        #set initial sort values based on max sort value of paragraphs by type
        for paragraph in paragraphs:
            current_type = paragraph["type"]
            current_component = paragraph["component_id"]
            current_category = paragraph["category_name"]

            if not "sort_order" in paragraph:
                continue

            if not current_component in paragraph_sorts[current_type]:
                paragraph_sorts[current_type][current_component] = {}
                paragraph_sorts[current_type][current_component][current_category] = paragraph["sort_order"]
            else:
                if not current_category in paragraph_sorts[current_type][current_component]:
                    paragraph_sorts[current_type][current_component][current_category] = paragraph["sort_order"]
                else:
                    paragraph_sorts[current_type][current_component][current_category] = max(paragraph_sorts[current_type][current_component][current_category], paragraph["sort_order"])

        #increment sort values by one to provide a starting point for new data
        for current_type in types:
            for current_component in components:
                if not current_component in paragraph_sorts[current_type]:
                    paragraph_sorts[current_type][current_component] = {}

                for current_category in categories:
                    if not current_category in paragraph_sorts[current_type][current_component]:
                        paragraph_sorts[current_type][current_component][current_category] = 1
                    else:
                        paragraph_sorts[current_type][current_component][current_category] += 1

        return paragraph_sorts

    def get_master_equipment_points(self, equipment_id):
        # find all equipment_points that are also master points
        return self.uow.run_list(self.equipment_points_table.get_all(equipment_id, index="equipment_id")
                                 .inner_join(self.uow.tables.component_points.get_all(True, index='master_point'),
                                    lambda a,b: a['component_point_id'] == b['id'])
                                 .map(lambda x: {
                                    'equipment_point_id': x['left']['id'],
                                    'code': x['right']['code'],
                                    'component_point_id': x['right']['id']
                                 }))

    def get_equipment_for_component(self, component_id):
        return self.uow.run_list(self.table.get_all(component_id, index='component_id'))

    def get_equipment_for_subcomponent(self, subcomponent_id):
        return self.uow.run_list(self.table.get_all(subcomponent_id, index='subcomponent_ids'))

    def get_values_for_numeric_point(self, equipment_point_id):
        point = self.uow.run(self.equipment_points_table.get(equipment_point_id))
        if not point:
            return None
        if point["point_type"] != "NP":
            return None

        if "values" not in point:
            return []

        return point["values"]

    def insert_value_for_numeric_point(self, equipment_point_id, model):
        point = self.uow.run(self.equipment_points_table.get(equipment_point_id))
        if point["point_type"] != "NP":
            raise Exception("Point not numeric point")

        if "values" not in point:
            point["values"] = []

        point["values"].append(model)

        self.uow.run(self.equipment_points_table.get(equipment_point_id).replace(point))

    def update_value_for_numeric_point(self, equipment_point_id, model):
        point = self.uow.run(self.equipment_points_table.get(equipment_point_id))
        if point["point_type"] != "NP":
            raise Exception("Point not numeric point")

        if "values" not in point:
            raise Exception("Value not found")

        point["values"] = [v for v in point["values"] if v["id"] != model["id"]]
        point["values"].append(model)

        self.uow.run(self.equipment_points_table.get(equipment_point_id).replace(point))

    def delete_value_for_numeric_point(self, equipment_point_id, value_id):
        point = self.uow.run(self.equipment_points_table.get(equipment_point_id))
        if point["point_type"] != "NP":
            raise Exception("Point not numeric point")

        if "values" not in point:
            raise Exception("Value not found")

        point["values"] = [v for v in point["values"] if v["id"] != value_id]

        self.uow.run(self.equipment_points_table.get(equipment_point_id).replace(point))

    def get_energy_equipment_points_for_equipment(self, equipment_id):
        return self.uow.run_list(self.equipment_points_table.get_all(equipment_id, index='equipment_id')
                                                            .has_fields('point_type')
                                                            .filter({'point_type': 'EP'}))

    def get_all_equipment_points(self):
        return self.uow.run_list(self.equipment_points_table)

    def update_equipment_point(self, equipment_point):
        """
        Uses a dictionary of an equipment point to update
        :param equipment_point: dictionary
        :return:
        """
        self.uow.run(self.equipment_points_table.update(equipment_point))

    def get_equipment_report_points_by_equipment_id(self, equipment_id):
        return self.uow.run_list(self.equipment_points_table.get_all(equipment_id, index="equipment_id")
                                                            .filter((r.row['units'].downcase() == 'kwh') |
                                                                    (r.row['units'].downcase() == 'btu')))

    def all_of_same_unit(self, syrx_nums):
        if len(syrx_nums) < 1:
            return True
        rv = self.uow.run_list(self.equipment_points_table.get_all(*syrx_nums, index='syrx_num')
                               .pluck('units')
                               .distinct())
        return len(rv) == 1

    def get_data_for_syrx_num(self, syrx_num):
        return self.uow.run_list(self.uow.tables.equipment_point_records.get_all(syrx_num, index='syrx_num'))

    def get_equipment_reporting_points(self, equipment_id):
        """
        Reporting points are equipment points that have certain units. If they can't be converted to BTU then they
        aren't reporting points
        :param equipment_id: ID of the equipment to retrieve points for
        :return: EquipmentPoints that can be reported on
        """

        return self.uow.run_list(self.equipment_points_table.get_all(equipment_id, index='equipment_id')
                                 .filter(r.row['units'].downcase().eq('kw')
                                         .or_(r.row['units'].downcase().eq('kwh'))
                                         .or_(r.row['units'].downcase().eq('cf/hr'))
                                         .or_(r.row['units'].downcase().eq('btuh'))
                                         .or_(r.row['units'].downcase().eq('hp'))
                                         .or_(r.row['units'].downcase().eq('tons'))
                                         .or_(r.row['units'].downcase().eq('cf'))
                                 ).pluck('id', 'point_code'))