from api.models.Group import Group
from api.models.QueryParameters import QueryResult
import rethinkdb as r

class GroupRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.groups

    def apply_query_parameters(self, query_parameters):
        q = self.table
        if query_parameters.filter is not None:
            for filter in query_parameters.filter["filters"]:
                if filter["operator"] == "startswith":
                    start = filter["value"].lower()
                    end = start
                    end = end[:-1] + chr(ord(end[-1]) + 1)
                    q = q.between(start, end, index="lower_name")
                else:
                    q = q.between(filter["value"].lower(), filter["value"].lower(), index="lower_name",
                                  right_bound="closed")
        for sort in query_parameters.sort:
            if sort["dir"] == "desc":
                q = q.order_by(index=r.desc("lower_name"))
            else:
                q = q.order_by(index=r.asc("lower_name"))

        data = self.uow.run_list(q.skip(query_parameters.skip).limit(query_parameters.take))
        total = self.uow.run(q.count())
        query_result = QueryResult(data, total)
        return query_result

    def get_group_by_id(self, group_id):
        group_raw = self.uow.run(self.table.get(group_id))
        if group_raw is None:
            return None
        group = Group(group_raw)

        group.accounts = self.uow.run_list(r.db("pathian").table("accounts").get_all(group_id, index="group_id"))

        return group

    def get_group_raw_by_id(self, group_id):
        return self.uow.run(self.table.get(group_id))

    def get_child_groups_of(self, group_id=None):
        if group_id is None:
            groups = self.uow.run_list(self.table.get_all(True, index="isRoot").order_by("lower_name"))
        else:
            groups = self.uow.run_list(self.table.get_all(group_id, index="parentIds").order_by("lower_name"))

        return groups

    def insert(self, group):
        try:
            del group.id
        except AttributeError:
            pass
        group.lower_name = group.name.lower()

        num = self.uow.run_list(self.uow.tables.next_group_num)[0]["next_group_num"]
        group.num = str(num)
        num += 1
        self.update_next_group_num(num)

        result = self.uow.run(self.table.insert(group.__dict__))
        group.id = result["generated_keys"][0]

        self.uow.run(self.uow.tables.flat_groups.insert({"group_id": group.id, "descendant_group_id": group.id}))

        # update naics_groups mappings
        insert_list = []
        naics_code_ancestors = self.uow.run_list(self.uow.tables.flat_naics_codes.get_all(group.naics_code, index='descendant'))
        for ancestor in naics_code_ancestors:
            insert_list.append({'code': ancestor['code'], 'group_descendant': group.id})

        self.uow.run(self.uow.tables.naics_groups_mapping.insert(insert_list))

        # update sic_groups mappings
        insert_list = []
        sic_code_ancestors = self.uow.run_list(self.uow.tables.flat_sic_codes.get_all(group.sic_code, index='descendant'))
        for ancestor in sic_code_ancestors:
            insert_list.append({'code': ancestor['code'], 'group_descendant': group.id})

        self.uow.run(self.uow.tables.sic_groups_mapping.insert(insert_list))

    def update_next_group_num(self, num):
        self.uow.run(self.uow.tables.next_group_num.update({"next_group_num": num}))

    def update(self, group):
        group.lower_name = group.name.lower()

        self.uow.run(self.table.get(group.id).update(group.__dict__))

        # update the niacs/sic trees

        # delete from both
        self.uow.run(self.uow.tables.naics_groups_mapping.get_all(group.id, index='group_descendant').delete())
        self.uow.run(self.uow.tables.sic_groups_mapping.get_all(group.id, index='group_descendant').delete())

        # update naics_groups mappings
        insert_list = []
        naics_code_ancestors = self.uow.run_list(self.uow.tables.flat_naics_codes.get_all(group.naics_code, index='descendant'))
        for ancestor in naics_code_ancestors:
            insert_list.append({'code': ancestor['code'], 'group_descendant': group.id})

        self.uow.run(self.uow.tables.naics_groups_mapping.insert(insert_list))

        # update sic_groups mappings
        insert_list = []
        sic_code_ancestors = self.uow.run_list(self.uow.tables.flat_sic_codes.get_all(group.sic_code, index='descendant'))
        for ancestor in sic_code_ancestors:
            insert_list.append({'code': ancestor['code'], 'group_descendant': group.id})

        self.uow.run(self.uow.tables.sic_groups_mapping.insert(insert_list))

    def add_root(self, child_id):
        group = self.uow.run(self.table.get(child_id))
        group["isRoot"] = True
        self.uow.run(self.table.get(group["id"]).update(group))

        descendants = self.uow.run_list(self.uow.tables.flat_groups.get_all(child_id, index="group_id")
                                        .filter({"descendant_group_id": child_id}))

        if len(descendants) == 0:
            self.uow.run(self.uow.tables.flat_groups.insert({"group_id": child_id, "descendant_group_id": child_id}))

        return dict(parent=None, child=group)

    def remove_root(self, child_id):
        group = self.uow.run(self.table.get(child_id))
        group["isRoot"] = False
        self.uow.run(self.table.get(group["id"]).update(group))

        return dict(parent=None, child=group)

    def add_child(self, parent_id, child_id):
        parent_group = self.uow.run(self.table.get(parent_id))
        parent_group["childIds"].append(child_id)
        self.uow.run(self.table.get(parent_id).update(parent_group))

        child_group = self.uow.run(self.table.get(child_id))
        child_group["parentIds"].append(parent_id)
        self.uow.run(self.table.get(child_id).update(child_group))

        try:
            insert_list = []
            parent_descendants = self.get_all_descendant_ids_as_set(parent_id)
            child_descendants = set(self.uow.run_list(self.uow.tables
                                                      .flat_groups
                                                      .get_all(child_id, index='group_id')
                                                      .map(lambda record: record['descendant_group_id'])))

            parent_descendant_union = parent_descendants | child_descendants
            descendants_to_add = parent_descendant_union - parent_descendants

            for descendant in descendants_to_add:
                insert_list.append({'group_id': parent_id, 'descendant_group_id': descendant})

            ancestors = self.uow.run_list(self.uow.tables.flat_groups.get_all(parent_id, index='descendant_group_id'))
            for ancestor in ancestors:
                if ancestor['group_id'] == parent_id:
                    continue
                ancestor_descendants = self.get_all_descendant_ids_as_set(ancestor['group_id'])
                ancestor_descendants_to_add = descendants_to_add - ancestor_descendants
                for descendant in ancestor_descendants_to_add:
                    insert_list.append({'group_id': ancestor['group_id'], 'descendant_group_id': descendant})
            self.uow.run(self.uow.tables.flat_groups.insert(insert_list))
        except:
            # TODO Add error handling
            pass

        return dict(parent=parent_group, child=child_group)

    def remove_child(self, parent_id, child_id):
        parent_group = self.uow.run(self.table.get(parent_id))

        try:
            parent_group["childIds"].remove(child_id)
        except ValueError:
            pass
        self.uow.run(self.table.get(parent_id).update(parent_group))

        child_group = self.uow.run(self.table.get(child_id))
        try:
            child_group["parentIds"].remove(parent_id)
        except ValueError:
            pass
        self.uow.run(self.table.get(child_id).update(child_group))

        new_descendants = set([parent_id])
        original_descendants = self.get_all_descendant_ids_as_set(parent_id)
        for child in parent_group['childIds']:
            new_descendants |= set(self.uow.run_list(self.uow.tables.flat_groups
                                                     .get_all(child, index='group_id')
                                                     .map(lambda record: record['descendant_group_id'])))

        descendants_to_delete = original_descendants - new_descendants
        if len(descendants_to_delete) > 0:
            for entry in descendants_to_delete:
                self.uow.run(self.uow.tables.flat_groups
                             .get_all(parent_id, index='group_id')
                             .filter({'descendant_group_id': entry})
                             .delete())
            self.recalc_parents_descendants(parent_id)

            parent_ids = self.uow.run(self.table.get(parent_id))['parentIds']
            for parent in parent_ids:
                self.recalc_parents_descendants(parent)

        return dict(parent=parent_group, child=child_group)

    def recalc_parents_descendants(self, group_id):
        current_group_descendants = self.get_all_descendant_ids_as_set(group_id)
        new_descendants = set([group_id])
        group_model = self.uow.run(self.table.get(group_id))
        for child in group_model['childIds']:
            new_descendants |= self.get_all_descendant_ids_as_set(child)
        descendants_to_remove = current_group_descendants - new_descendants
        if len(descendants_to_remove) > 0:
            for entry in descendants_to_remove:
                self.uow.run(self.uow.tables.flat_groups
                             .get_all(group_id, index='group_id')
                             .filter({'descendant_group_id': entry})
                             .delete())
            for parent in group_model['parentIds']:
                self.recalc_parents_descendants(parent)

    def get_groups_by_account_ids(self, account_ids):
        group_dict = {}
        for a in account_ids:
            group_id = self.uow.run(self.uow.tables.accounts.get(a))['group_id']
            group_dict[a] = self.uow.run(self.table.get(group_id))['name']
        return group_dict

    def get_accounts(self, group_id):
        accounts = self.uow.run_list(self.uow.tables.accounts.get_all(group_id, index='group_id'))
        return accounts

    def get_descendants(self, group_id):
        entry = self.uow.run_list(self.uow.tables.flat_groups
                                  .get_all(group_id, index='group_id')
                                  .map(lambda record: record['descendant_group_id']))
        if len(entry) < 1:
            return entry

        descendants = self.uow.run_list(self.table.get_all(*entry).pluck('id', 'name'))
        return descendants

    def get_by_naics_code(self, naics_code):
        groups = self.uow.run_list(self.table.get_all(naics_code, index="naics_code"))
        descendants = self.uow.run_list(self.uow.tables.naics_groups_mapping
                                        .get_all(naics_code, index='code')
                                        .map(lambda record: record['group_descendant']))
        for entry in descendants:
            groups.append(self.uow.run(self.table.get(entry)))
        return groups

    def get_by_naics_codes(self, naics_codes):
        groups = self.uow.run_list(self.table.get_all(*naics_codes, index='naics_code'))
        return groups

    def get_by_sic_codes(self, sic_codes):
        groups = self.uow.run_list(self.table.get_all(*sic_codes, index='sic_code'))
        return groups

    def get_all(self, groups=None):
        if groups is None:
            group_list = self.uow.run_list(self.table)
            return group_list
        elif len(groups) < 1:
            return []
        group_list = self.uow.run_list(self.table.get_all(*groups))
        return group_list

    def get_batch(self, batch_size, starting_position):
        if batch_size is None:
            batch_size = 500

        if starting_position is None:
            starting_position = 0

        group_list = self.uow.run_list(self.table.skip(starting_position).limit(batch_size))

        return group_list

    def get_by_sic_code(self, sic_code):
        groups = self.uow.run_list(self.table.get_all(sic_code, index="sic_code"))

        descendants = self.uow.run_list(self.uow.tables.sic_groups_mapping
                                        .get_all(sic_code, index='code')
                                        .map(lambda record: record['group_descendant']))
        for entry in descendants:
            groups.append(self.uow.run(self.table.get(entry)))
        return groups

    def get_all_descendant_ids_as_set(self, id):
        return set(self.uow.run_list(self.uow.tables.flat_groups
                                     .get_all(id, index='group_id')
                                     .map(lambda record: record['descendant_group_id'])))

    def insert_flat_groups(self, flat_groups):
        self.uow.run(self.uow.tables.flat_groups.insert(flat_groups))

    def insert_many(self, groups):
        self.uow.run(self.table.insert(groups))

    def get_children_of_naics_code(self, naics_code):
        groups = self.uow.run_list(self.table.get_all(naics_code, index='naics_code'))
        return groups

    def get_children_of_sic_code(self, sic_code):
        groups = self.uow.run_list(self.table.get_all(sic_code, index='sic_code'))
        return groups

    def delete_flat_groups(self):
        self.uow.run(self.uow.tables.flat_groups.delete())