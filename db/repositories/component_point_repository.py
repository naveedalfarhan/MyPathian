from api.models.QueryParameters import QueryResult
import rethinkdb as r


class ComponentPointRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.component_points

    def apply_query_parameters_by_component_id(self, component_id, query_parameters):
        q = self.table.get_all(component_id, index="component_id")
        q = q.order_by("component_point_num")
        cursor = q.skip(query_parameters.skip).limit(query_parameters.take)

        data = self.uow.run_list(cursor)
        total = self.uow.run(q.count())
        query_result = QueryResult(data, total)
        return query_result

    def get_points_for_component_id(self, component_id, point_type=None):
        if point_type is None:
            q = self.table.get_all(component_id, index="component_id")
        else:
            q = self.table.get_all([component_id, point_type], index="component_id_point_type")
        q = q.order_by("component_point_num")
        data = self.uow.run_list(q)
        return data

    def get_points_for_component_ids(self, component_ids):
        q = self.table.get_all(*component_ids, index="component_id")
        q = q.order_by("component_point_num").group("component_id").ungroup()
        data = self.uow.run_list(q)
        data = dict((x["group"], x["reduction"]) for x in data)
        return data

    def get_all_available_paragraphs(self, component_ids):

        ancestor_ids = self.get_ancestor_component_ids(component_ids)

        component_ids = list(set(component_ids).union(ancestor_ids))

        paragraphs_query = (self.uow.tables.paragraph_definitions.get_all(*component_ids, index="component_id")
                            .order_by("num"))
        paragraphs = self.uow.run_list(paragraphs_query)

        components_query = (self.uow.tables.components.get_all(*component_ids).pluck('id', 'num', 'description')
                            .order_by('num'))
        components = self.uow.run_list(components_query)

        return {"components":components, "paragraphs": paragraphs}


    def get_ancestor_component_ids(self, component_ids):
        parent_ids = self.uow.run_list(self.uow.tables.components.get_all(*component_ids).pluck('structure_parent_id')
                                       .filter(lambda x: x.has_fields('structure_parent_id')))

        if len(parent_ids) is 0:
            return set()

        parent_ids = [component["structure_parent_id"] for component in parent_ids]

        return set(parent_ids).union(self.get_ancestor_component_ids(parent_ids))


    def insert(self, component_id, component_point):
        try:
            del component_point.id
        except AttributeError:
            pass

        component = self.uow.run(self.uow.tables.components.get(component_id))

        component_point.point_type_caption = {"EP": "Energy Point",
                                              "CP": "Calculated Point",
                                              "PP": "Position Point",
                                              "NP": "Numeric Point",
                                              "BP": "Binary Point",
                                              "VP": "Variable Point"}[component_point.point_type]

        if component_point.point_type == "BP":
            component_point.units = None

        component_point.component_point_num = component["num"].replace(" ", "") + "-" + component_point.point_type

        next_num_field_name = "next_" + component_point.point_type

        if next_num_field_name not in component:
            component_point.component_point_num += "-001"
            component[next_num_field_name] = "002"
        else:
            # the newly added component must be 3 digits
            # covers any previous values that are strings
            component[next_num_field_name] = int(component[next_num_field_name])

            length_of_num = len(str(abs(component[next_num_field_name])))
            if length_of_num == 1:  # add 2 zeros
                next_component_num = "00" + str(component[next_num_field_name])
            elif length_of_num == 2:  # add 1 zero
                next_component_num = "0" + str(component[next_num_field_name])
            else:  # no extra zeros needed
                next_component_num = str(component[next_num_field_name])
            component_point.component_point_num += "-" + next_component_num
            component[next_num_field_name] += 1

        self.uow.run(self.uow.tables.components.get(component_id).update(component))

        component_point.component_id = component_id
        self.uow.run(self.table.insert(component_point.__dict__))

    def update(self, component_point):
        if component_point.point_type == "BP":
            component_point.units = None

        self.uow.run(self.table.update(component_point.__dict__))

    def delete(self, point_id):
        self.uow.run(self.table.get(point_id).delete())

    def get_weatherstation_ids_for_syrx_numbers(self, syrx_nums):
        if len(syrx_nums) > 0:
            l = self.uow.run_list(self.uow.tables.equipment_points
                                  .get_all(*syrx_nums, index="syrx_num")
                                  .eq_join("equipment_id", self.uow.tables.equipment).zip()
                                  .eq_join("group_id", self.uow.tables.groups).zip()
                                  .pluck("syrx_num", "weatherstation_id"))
            l = [x for x in l if "weatherstation_id" in x]
        else:
            l = []
        d = dict((x["syrx_num"], x["weatherstation_id"]) for x in l)
        return d

    def get_all(self):
        return self.uow.run_list(self.table)

    def insert_bulk(self, points):
        self.uow.run(self.table.insert(points, durability="hard"))
        self.uow.run(self.table.insert(points))

    def get_by_component_point_num(self, point_id):
        return self.uow.run_list(self.table.get_all(point_id, index='component_point_num'))

    def set_master_point(self, point_id):
        return self.uow.run(self.table.get(point_id).update({'master_point': True}))

    def revoke_master_point(self, point_id):
        return self.uow.run(self.table.get(point_id).update({'master_point': False}))

    def get_by_component_point_id(self, point_id):
        return self.uow.run(self.table.get(point_id))

    def get_master_points_by_component_ids(self, component_ids):
        # component_ids should be in the form [[component_id, True], [component_id, True], [component_id, True]...]
        points = self.uow.run_list(self.table.get_all(*component_ids, index='component_id_master_point'))
        return points

    def delete_component_master_point_mappings_for_point(self, master_point_num):
        return self.uow.run(self.uow.tables.component_master_point_mappings.get_all(master_point_num, index='master_point_num').delete())

    def get_points_by_type(self, point_type):
        return self.uow.run_list(self.table.get_all(point_type, index="point_type"))

    @staticmethod
    def unit_map_func(x):
        return x['units']

    def all_of_same_unit(self, component_ids):
        if len(component_ids) < 1:
            return True
        rv = self.uow.run_list(self.table.get_all(*component_ids)
                               .has_fields('units')
                               .map(self.unit_map_func)
                               .distinct())
        return len(rv) == 1

    def group_by_units(self, component_ids):
        if len(component_ids) < 1:
            return []
        rv = self.uow.run_list(self.table.get_all(*component_ids)
                               .group(self.unit_map_func)
                               .ungroup())
        return rv

    @staticmethod
    def syrx_map_func(x):
        return x['syrx_num']

    def get_syrx_nums_for_component_point(self, component_point_id):
        rv = self.uow.run_list(self.uow.tables.equipment_points.get_all(component_point_id, index='component_point_num')
                               .map(self.syrx_map_func))
        return rv

    @staticmethod
    def has_decimal_func(x):
        return r.expr(x['formula']).split('.').count().ge(2)

    def get_all_cp_with_decimal(self):
        return self.uow.run_list(self.table.get_all('CP', index='point_type').filter(self.has_decimal_func))

    def get_points_by_code(self, code):
        return self.uow.run_list(self.table.filter({'code': code}))