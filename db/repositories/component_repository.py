from collections import defaultdict
from api.models.Component import Component
from api.models.QueryParameters import QueryResult
import rethinkdb as r

class ComponentRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.components
        self.component_issues_table = uow.tables.component_issues
        self.component_tasks_table = uow.tables.component_tasks

    def get_all(self):
        return self.uow.run_list(self.table)

    def get_by_id(self, component_id):
        component_raw = self.uow.run(self.table.get(component_id))
        component = Component(component_raw)
        return component

    def get_structure_children_of(self, component_id=None):
        if component_id is None:
            components = self.uow.run_list(self.table
                                           .order_by(index="num")
                                           .filter(~r.row.has_fields("structure_parent_id")))
        else:
            components = self.uow.run_list(self.table
                                           .get_all(component_id, index="structure_parent_id")
                                           .order_by("num"))

        return components

    def get_mapping_children_of(self, component_id=None):
        if component_id is None:
            components = self.uow.run_list(self.table
                                           .order_by(index="num")
                                           .filter(r.row["mapping_root"].eq(True)))
        else:
            components = self.uow.run_list(self.table
                                           .get_all(component_id, index="mapping_parent_ids")
                                           .order_by("num"))

        return components

    def get_mapping_parents_of(self, component_id):
        return self.uow.run_list(self.table.get_all(component_id, index='mapping_child_ids'))

    def get_structure_equipment_children_of(self, component_id=None):
        if component_id is None:
            components = self.uow.run_list(self.table
                                           .order_by(index="num")
                                           .filter(~r.row.has_fields("structure_parent_id")))
            for c in components:
                c["id"] = "component_" + c["id"]
                c["name"] = c["num"] + " " + c["description"]

        elif component_id[:10] == "component_":
            component_id = component_id[10:]
            components = self.uow.run_list(self.table
                                           .get_all(component_id, index="structure_parent_id")
                                           .order_by("num"))
            for c in components:
                c["id"] = "component_" + c["id"]
                c["name"] = c["num"] + " " + c["description"]
            equipment = self.uow.run_list(self.uow.tables.equipment
                                          .get_all(component_id, index="component_id")
                                          .order_by("name"))
            for e in equipment:
                e["id"] = "equipment_" + e["id"]
            components += equipment

        else:
            components = []

        return components

    def get_equipment_for_components(self, components, component_id):
        for component in components:
            if not component["has_children"]:
                component['has_children'] = self.uow.run(self.uow.tables.equipment
                                                         .get_all(component['id'][2:], index='component_id')
                                                         .count()) > 0

        if component_id:
            equipment = self.uow.run_list(self.uow.table.equipment.get_all(component_id, index='component_id')
                                          .map(lambda record: {'name': record['name'],
                                                               'group_id': record['group_id'],
                                                               'id': record['id'],
                                                               'num': record['num'],
                                                               'has_children': record['subcomponent_ids'].count() > 0}))
            grouped = defaultdict(dict)
            if len(equipment) > 0:
                equipment_group_ids = map(lambda record: record['group_id'], equipment)
                groups = self.uow.run_list(self.uow.table.groups.get_all(*equipment_group_ids))

                for g in groups:
                    grouped[g['id']] = g

            for e in equipment:
                e["id"] = "e_" + e['group_id'] + "_" + e['num']
                e['name'] = grouped[e['group_id']]['name'] + "_" + e['name']
            components += equipment

        return components

    def get_child_components_and_equipment(self, component_id=None):
        if component_id is None:
            components = self.uow.run_list(
                self.table.order_by(index="num").filter(~r.row.has_fields("structure_parent_id"))
                    .map(lambda record: {'description': record['description'], 'id': 'c_' + record['id'],
                                         'mapping_root': record['mapping_root'], 'num': record['num'],
                                         'protected': record['num'],
                                         'structure_child_ids': record['structure_child_ids'],
                                         'structure_parent_id': record['structure_parent_id'],
                                         'name': record['num'] + ' ' + record['description'],
                                         'has_children': record['structure_child_ids'].count() > 0}))
            components = self.get_equipment_for_components(components, component_id)

        elif component_id[:2] == "c_":
            component_id = component_id[2:]
            components = self.uow.run_list(
                self.table.get_all(component_id, index="structure_parent_id")
                    .map(lambda record: {'description': record['description'], 'id': 'c_' + record['id'],
                                         'mapping_root': record['mapping_root'], 'num': record['num'],
                                         'protected': record['num'],
                                         'structure_child_ids': record['structure_child_ids'],
                                         'structure_parent_id': record['structure_parent_id'],
                                         'name': record['num'] + ' ' + record['description'],
                                         'has_children': record['structure_child_ids'].count() > 0}).order_by("num"))
            components = self.get_equipment_for_components(components, component_id)

        elif component_id[:2] == "e_":
            component_id = component_id[2:]
            split_id = component_id.split('_')
            equipment = self.uow.run_list(self.uow.tables.equipment
                                          .get_all([split_id[0], split_id[1]], index='combined_tree'))[0]
            component = self.uow.run(self.table.get(equipment['component_id']))

            components = [
                {'id': 's_' + equipment['group_id'] + "_" + equipment['num'] + "_" + equipment['component_id'],
                 'name': component['num'] + " " + component['description'],
                 'has_children': False}
            ]

            if len(equipment['subcomponent_ids']) > 0:
                subcomponents = self.uow.run(self.table.get_all(*equipment['subcomponent_ids']))
                grouped = defaultdict(dict)
                for s in subcomponents:
                    grouped[s['id']] = s

            for s in equipment['subcomponent_ids']:
                components.append({'id': 's_' + equipment['group_id'] + "_" + equipment['num'] + '_' + s,
                                   'name': grouped[s]['num'] + ' ' + grouped[s]['description'],
                                   'has_children': False})
        elif component_id[:2] == 's_':
            component_id = component_id[2:]
            split_id = component_id.split('_')
            component_points = self.uow.run_list(self.uow.tables.component_points
                                                 .get_all(split_id[2], index='component_id')
                                                 .map(lambda record: record['id']))

            if len(component_points) > 0:
                points = self.uow.run_list(self.uow.tables.equipment_points
                                           .get_all(*component_points, index='component_point_id'))
            else:
                points = []

            components = [{'id': p['id'], 'syrx_num': p['syrx_num']} for p in points]
        else:
            components = []

        return components

    def insert(self, component, no_parent_processing=False):
        try:
            del component.id
        except AttributeError:
            pass

        if no_parent_processing:
            result = self.uow.run(self.table.insert(component.__dict__))
            component.id = result["generated_keys"][0]
        else:
            parent_component = self.uow.run(self.table.get(component.structure_parent_id))

            component.num = parent_component["num"]
            if "next_component_num" not in parent_component:
                component.num += "-001"
                parent_component["next_component_num"] = 2
            else:
                # the newly added component must be 3 digits
                length_of_num = len(str(abs(parent_component["next_component_num"])))
                if length_of_num == 1:  # add 2 zeros
                    next_component_num = "00" + str(parent_component["next_component_num"])
                elif length_of_num == 2:  # add 1 zero
                    next_component_num = "0" + str(parent_component["next_component_num"])
                else:  # no extra zeros needed
                    next_component_num = str(parent_component["next_component_num"])
                component.num += "-" + next_component_num
                parent_component["next_component_num"] += 1


            if "structure_child_ids" not in parent_component:
                parent_component["structure_child_ids"] = []

            result = self.uow.run(self.table.insert(component.__dict__))
            component.id = result["generated_keys"][0]

            parent_component["structure_child_ids"].append(component.id)
            self.uow.run(self.table.get(parent_component["id"]).update(parent_component))

        return component

    def insert_bulk(self, components):
        self.uow.run(self.table.insert(components, durability="hard"))

    def update_bulk(self, components):
        self.uow.run(self.table.update(components))

    def update(self, component):
        self.uow.run(self.table.get(component.id).update(component.__dict__))

    def update_raw(self, component):
        self.uow.run(self.table.get(component["id"]).update(component))

    def delete(self, component_id):
        component = self.uow.run(self.table.get(component_id))
        # if the component isn't a root component, then delete it's reference from it's parent
        if component['structure_parent_id']:
            parent_component = self.uow.run(self.table.get(component["structure_parent_id"]))

            try:
                parent_component["structure_child_ids"].remove(component["id"])
            except ValueError:
                pass
            except AttributeError:
                pass

            self.uow.run(self.table.update(parent_component))
        self.uow.run(self.table.get(component_id).delete())

    def add_mapping_child(self, parent_id, child_id):
        parent_component = self.uow.run(self.table.get(parent_id))
        try:
            parent_component["mapping_child_ids"].append(child_id)
        except KeyError:
            parent_component["mapping_child_ids"] = [child_id]
        if "mapping_parent_ids" not in parent_component:
            parent_component["mapping_parent_ids"] = []
        self.uow.run(self.table.get(parent_id).update(parent_component))

        child_component = self.uow.run(self.table.get(child_id))
        try:
            child_component["mapping_parent_ids"].append(parent_id)
        except KeyError:
            child_component["mapping_parent_ids"] = [parent_id]
        if "mapping_child_ids" not in child_component:
            child_component["mapping_child_ids"] = []
        self.uow.run(self.table.get(child_id).update(child_component))

        return dict(parent=parent_component, child=child_component)

    def remove_mapping_child(self, parent_id, child_id):
        parent_component = self.uow.run(self.table.get(parent_id))
        try:
            parent_component["mapping_child_ids"].remove(child_id)
        except ValueError:
            pass
        self.uow.run(self.table.get(parent_id).update(parent_component))

        child_component = self.uow.run(self.table.get(child_id))
        try:
            child_component["mapping_parent_ids"].remove(parent_id)
        except ValueError:
            pass
        self.uow.run(self.table.get(child_id).update(child_component))

        return dict(parent=parent_component, child=child_component)

    def add_mapping_root(self, child_id):
        child_component = self.uow.run(self.table.get(child_id))
        if "mapping_parent_ids" not in child_component:
            child_component["mapping_parent_ids"] = []
        if "mapping_child_ids" not in child_component:
            child_component["mapping_child_ids"] = []
        child_component["mapping_root"] = True
        self.uow.run(self.table.get(child_id).update(child_component))

        return dict(child=child_component)

    def remove_mapping_root(self, child_id):
        child_component = self.uow.run(self.table.get(child_id))
        child_component["mapping_root"] = False
        self.uow.run(self.table.get(child_id).update(child_component))

        return dict(child=child_component)

    def insert_component_issue(self, model):
        try:
            del model.id
        except AttributeError:
            pass

        component = self.uow.run(self.uow.tables.components.get(model.component_id))

        num = component["num"].replace(" ", "") + "-CI"

        next_num_field_name = "next_CI"

        if next_num_field_name not in component:
            num += "-1"
            component[next_num_field_name] = "2"
        else:
            num += "-" + component[next_num_field_name]
            component[next_num_field_name] = str(int(component[next_num_field_name]) + 1)
        self.uow.run(self.uow.tables.components.update(component))

        model.num = num

        self.uow.run(self.component_issues_table.insert(model.__dict__))

    def update_component_issue(self, model):
        self.uow.run(self.component_issues_table.update(model.__dict__))

    def delete_component_issue(self, component_issue_id):
        self.uow.run(self.component_issues_table.get(component_issue_id).delete())

    def get_component_issues_table(self, component_id, query_parameters):
        q = self.component_issues_table.get_all(component_id, index="component_id")
        q = q.order_by("num")
        cursor = q.skip(query_parameters.skip).limit(query_parameters.take)

        data = self.uow.run_list(cursor)
        total = self.uow.run(q.count())
        query_result = QueryResult(data, total)
        return query_result

    def get_component_issues(self, component_ids):
        return list(self.uow.run(self.component_issues_table.get_all(*component_ids, index="component_id")))

    def insert_component_task(self, model):
        try:
            del model.id
        except AttributeError:
            pass

        component = self.uow.run(self.uow.tables.components.get(model.component_id))

        num = component["num"].replace(" ", "") + "-CT"

        next_num_field_name = "next_CT"

        if next_num_field_name not in component:
            num += "-1"
            component[next_num_field_name] = "2"
        else:
            num += "-" + component[next_num_field_name]
            component[next_num_field_name] = str(int(component[next_num_field_name]) + 1)
        self.uow.run(self.uow.tables.components.update(component))

        model.num = num

        self.uow.run(self.component_tasks_table.insert(model.__dict__))

    def update_component_task(self, model):
        self.uow.run(self.component_tasks_table.update(model.__dict__))

    def delete_component_task(self, component_task_id):
        self.uow.run(self.component_tasks_table.get(component_task_id).delete())

    def get_component_tasks(self, component_ids):
        return list(self.uow.run(self.component_tasks_table.get_all(*component_ids, index="component_id")))

    def get_component_tasks_table(self, component_id, query_parameters):
        q = self.component_tasks_table.get_all(component_id, index="component_id")
        q = q.order_by("num")
        cursor = q.skip(query_parameters.skip).limit(query_parameters.take)

        data = self.uow.run_list(cursor)
        total = self.uow.run(q.count())
        query_result = QueryResult(data, total)
        return query_result

    def get_component_and_ancestor_ids(self, component_id):
        # initialize the list with the passed in component
        component_ids = [component_id]

        # fetch the passed in component
        current_component = self.uow.run(self.table.get(component_id))

        # while the current component has a parent
        while 'structure_parent_id' in current_component and current_component['structure_parent_id'] is not None:
            # fetch the parent component
            current_component_id = current_component['structure_parent_id']
            current_component = self.uow.run(self.table.get(current_component_id))

            # add the parent's id to the list
            component_ids.append(current_component_id)

        return component_ids

    def get_all_as_cursor(self):
        return self.uow.run(self.table)

    def set_component_master_point(self, component_id, master_point):
        return self.uow.run(self.table.get(component_id).update({'master_point': master_point.__dict__}))

    def insert_flat_components(self, flat_components):
        self.uow.run(self.uow.tables.flat_components.insert(flat_components))

    def insert_component_master_point_mappings(self, mappings):
        self.uow.run(self.uow.tables.component_master_point_mappings.insert(mappings))

    def get_component_ancestors(self, component_id):
        return self.uow.run_list(self.uow.tables.flat_components.get_all(component_id, index='descendant_component_id'))

    def get_component_master_point_mappings(self, component_id):
        return self.uow.run_list(self.uow.tables.component_master_point_mappings.get_all(component_id, index='component_id'))

    def insert_new_component_master_point_mappings(self, component_id, master_point_num):
        # get the components ancestors
        component_ancestors = self.get_component_ancestors(component_id)

        # create the mapping list to insert in the database
        mapping_list = [{"component_id": ancestor["component_id"],
                         "master_point_num": master_point_num} for ancestor in component_ancestors]

        return self.uow.run(self.uow.tables.component_master_point_mappings.insert(mapping_list))

    @staticmethod
    def descendant_component_id_mapping_func(record):
        return record['descendant_component_id']

    def get_component_descendants(self, component_id):
        return self.uow.run_list(self.uow.tables.flat_components.get_all(component_id, index='component_id').map(self.descendant_component_id_mapping_func))

    def get_by_number(self, component_num):
        component_list = self.uow.run_list(self.table.get_all(component_num, index='num'))
        if len(component_list) > 0:
            return Component(component_list[0])
        else:
            return None