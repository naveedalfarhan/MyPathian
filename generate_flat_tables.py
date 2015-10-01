from db.uow import UoW


class FlatTableGenerator:
    def __init__(self):
        self.uow = UoW(False)
        self.desc_dict = []

    def get_group_descendants(self, node_id):
        descendants = self.check_existence(node_id)
        if descendants:
            return descendants['descendants']
        child_list = [node_id]
        group = self.uow.groups.get_group_raw_by_id(node_id)
        if group:
            for child in group['childIds']:
                child_list.append(child)
                child_descendants = self.get_group_descendants(child)
                self.desc_dict.append({'id': child, 'descendants': list(set(child_descendants))})
                if len(child_descendants) > 0:
                    child_list += child_descendants
        return child_list

    def check_existence(self, group_id):
        for r in self.desc_dict:
            if r['id'] == group_id:
                return r
        return {}

    def generate_flat_groups(self):
        print "Deleting current flat table..."
        self.uow.groups.delete_flat_groups()

        print "Getting groups..."
        groups_list = self.uow.groups.get_all()

        print "Mapping descendants..."
        descendants = map(lambda g:
                          {"id": g["id"],
                           "descendants": set(g["childIds"]) | set([g["id"]])}, groups_list)
        num_descendants = len(descendants)

        print "Mapping descendants dictionary..."
        descendants_dict = dict((d["id"], d) for d in descendants)

        non_complete_descendants = dict(descendants_dict)

        print str(len(non_complete_descendants)) + " groups"
        pass_counter = 0
        while len(non_complete_descendants) > 0:
            this_round_of_descendants = non_complete_descendants.values()

            for d in this_round_of_descendants:
                descendants_to_union = set()
                for group_id in d["descendants"]:
                    if group_id in descendants_dict:
                        group_descendants = descendants_dict[group_id]["descendants"]
                    else:
                        group_descendants = set()
                    descendants_to_union |= group_descendants
                if len(descendants_to_union - d["descendants"]) == 0:
                    del non_complete_descendants[d["id"]]
                else:
                    d["descendants"] |= descendants_to_union
            pass_counter += 1
            print "Pass " + str(pass_counter) + " complete"
            print str(len(non_complete_descendants)) + " groups remaining"

        print "Convert descendants to flat list..."

        flat_list = []
        for g in descendants:
            for d in g["descendants"]:
                flat_list.append({"group_id": g["id"], "descendant_group_id": d})

        print "Begin inserting flat list records..."

        num_flat_list = len(flat_list)
        for x in range(0, num_flat_list, 2000):
            batch = flat_list[x:(x + 2000)]
            try:
                self.uow.groups.insert_flat_groups(batch)
            except Exception as e:
                print("error")
                raise
            print "Inserted " + str(x + len(batch)) + "/" + str(num_flat_list) + " group/descendant relationships"

        print "Finished inserting groups records!"

    def get_naics_descendants(self, node_code):
        child_list = []
        children = self.uow.naics.get_by_parent(node_code)
        for child in children:
            child_list.append(child["code"])
            child_descendants = self.get_naics_descendants(child["code"])
            if len(child_descendants) > 0:
                child_list += child_descendants
        return child_list

    def get_group_descendants_for_naics(self, desc):
        group_desc = []
        for d in desc:
            groups = self.uow.groups.get_by_naics_code(d)
            for group in groups:
                group_descendants = self.uow.groups.get_descendants(group['id'])
                for g in group_descendants:
                    group_desc.append(g['id'])
                group_desc.append(group['id'])
        return group_desc

    def generate_flat_naics_codes(self):
        print "Deleting previous table entries..."
        self.uow.naics.delete_flat_table()

        print "Getting NAICS codes..."
        naics_list = self.uow.naics.get_all()

        print "Mapping descendants..."
        temp_dict = {}
        for code in naics_list:
            if not code['parent_code']:
                if code['code'] not in temp_dict:
                    temp_dict[code['code']] = set([code['code']])
            else:
                if code['parent_code'] not in temp_dict:
                    temp_dict[code['parent_code']] = set([code['parent_code'], code['code']])
                else:
                    temp_dict[code['parent_code']] = set(temp_dict[code['parent_code']] | set([code['code']]))
                if code['code'] not in temp_dict:
                    temp_dict[code['code']] = set([code['code']])
        descendants = []
        for entry in temp_dict:
            descendants.append({'code': entry, 'descendants': temp_dict[entry]})
        num_descendants = len(descendants)

        print "Mapping descendants dictionary..."
        descendants_dict = dict((d['code'], d) for d in descendants)

        non_complete_descendants = dict(descendants_dict)

        print str(len(non_complete_descendants)) + " NAICS codes"
        pass_counter = 0
        groups_mapping = []
        while len(non_complete_descendants) > 0:
            this_round_of_descendants = non_complete_descendants.values()

            for d in this_round_of_descendants:
                descendants_to_union = set()
                for naics_code in d['descendants']:
                    if naics_code in descendants_dict:
                        naics_descendants = descendants_dict[naics_code]['descendants']
                    else:
                        naics_descendants = set()
                    descendants_to_union |= naics_descendants
                if len(descendants_to_union - d['descendants']) == 0:
                    del non_complete_descendants[d['code']]
                    groups = self.uow.groups.get_by_naics_codes(d["descendants"])
                    for g in groups:
                        groups_mapping.append({'code': d['code'], 'group_descendant': g["id"]})
                else:
                    d['descendants'] |= descendants_to_union
            pass_counter += 1
            print "Pass " + str(pass_counter) + " complete"
            print str(len(non_complete_descendants)) + " NAICS codes remaining"

        print "Convert descendants to flat list..."

        flat_list = []
        for g in descendants:
            for d in g['descendants']:
                flat_list.append({'code': g['code'], 'descendant': d})

        print "Begin inserting flat list records..."

        num_flat_list = len(flat_list)
        for x in range(0, num_flat_list, 2000):
            batch = flat_list[x:(x + 2000)]
            try:
                self.uow.naics.insert_into_flat_naics(batch)
            except Exception as e:
                print "error"
                raise
            print "Inserted " + str(x + len(batch)) + "/" + str(num_flat_list) + " NAICS code/descendant relationships"

        for x in range(0, len(groups_mapping), 2000):
            batch = groups_mapping[x:(x + 2000)]
            try:
                self.uow.naics.insert_into_mapping_table(batch)
            except Exception as e:
                print "error"
                raise
            print "Inserted " + str(x + len(batch)) + "/" + str(len(groups_mapping)) + " NAICS code/group mappings"

        print "Finished inserting NAICS Codes."


    def get_sic_descendants(self, node_code):
        child_list = []
        children = self.uow.sic.get_by_parent(node_code)
        for child in children:
            child_list.append(child["code"])
            child_descendants = self.get_sic_descendants(child["code"])
            if len(child_descendants) > 0:
                child_list += child_descendants
        return child_list

    def get_group_descendants_for_sic(self, desc):
        group_desc = []
        for d in desc:
            groups = self.uow.groups.get_by_sic_code(d)
            for group in groups:
                group_descendants = self.uow.groups.get_descendants(group['id'])
                for g in group_descendants:
                    group_desc.append(g['id'])
                group_desc.append(group['id'])
        return group_desc

    def generate_flat_sic_codes(self):
        print "Deleting previous table entries..."
        self.uow.sic.delete_flat_table()

        print "Getting SIC codes..."
        sic_list = self.uow.sic.get_all()

        print "Mapping descendants..."
        temp_dict = {}
        for code in sic_list:
            if not code['parent_code']:
                if code['code'] not in temp_dict:
                    temp_dict[code['code']] = set([code['code']])
            else:
                if code['parent_code'] not in temp_dict:
                    temp_dict[code['parent_code']] = set([code['parent_code'], code['code']])
                else:
                    temp_dict[code['parent_code']] = set(temp_dict[code['parent_code']] | set([code['code']]))
                if code['code'] not in temp_dict:
                    temp_dict[code['code']] = set([code['code']])
        descendants = []
        for entry in temp_dict:
            descendants.append({'code': entry, 'descendants': temp_dict[entry]})
        num_descendants = len(descendants)

        print "Mapping descendants dictionary..."
        descendants_dict = dict((d['code'], d) for d in descendants)

        non_complete_descendants = dict(descendants_dict)

        print str(len(non_complete_descendants)) + " SIC codes"
        pass_counter = 0
        groups_mapping = []
        while len(non_complete_descendants) > 0:
            this_round_of_descendants = non_complete_descendants.values()

            for d in this_round_of_descendants:
                descendants_to_union = set()
                for sic_code in d['descendants']:
                    if sic_code in descendants_dict:
                        sic_descendants = descendants_dict[sic_code]['descendants']
                    else:
                        sic_descendants = set()
                    descendants_to_union |= sic_descendants
                if len(descendants_to_union - d['descendants']) == 0:
                    del non_complete_descendants[d['code']]
                    groups = self.uow.groups.get_by_sic_codes(d["descendants"])
                    for g in groups:
                        groups_mapping.append({'code': d['code'], 'group_descendant': g["id"]})
                else:
                    d['descendants'] |= descendants_to_union
            pass_counter += 1
            print "Pass " + str(pass_counter) + " complete"
            print str(len(non_complete_descendants)) + " SIC codes remaining"

        print "Convert descendants to flat list..."

        flat_list = []
        for g in descendants:
            for d in g['descendants']:
                flat_list.append({'code': g['code'], 'descendant': d})

        print "Begin inserting flat list records..."

        num_flat_list = len(flat_list)
        for x in range(0, num_flat_list, 2000):
            batch = flat_list[x:(x+2000)]
            try:
                self.uow.sic.insert_into_flat_sic(batch)
            except Exception as e:
                print "error"
                raise
            print "Inserted " + str(x + len(batch)) + "/" + str(num_flat_list) + " SIC code/descendant relationships"

        for x in range(0, len(groups_mapping), 2000):
            batch = groups_mapping[x:(x + 2000)]
            try:
                self.uow.sic.insert_into_mapping_table(batch)
            except Exception as e:
                print "error"
                raise
            print "Inserted " + str(x + len(batch)) + "/" + str(len(groups_mapping)) + " SIC code/group mappings"

        print "Finished inserted SIC codes."

    def generate_flat_components(self):
        print "Getting components..."
        components_list = self.uow.components.get_all()

        print "Mapping descendants..."
        descendants = map(lambda g:
                          {"id": g["id"],
                           "descendants": set(g["structure_child_ids"]) | set([g["id"]])}, components_list)
        num_descendants = len(descendants)

        print "Mapping descendants dictionary..."
        descendants_dict = dict((d["id"], d) for d in descendants)

        non_complete_descendants = dict(descendants_dict)

        print str(len(non_complete_descendants)) + " components"
        pass_counter = 0

        point_mappings = []
        while len(non_complete_descendants) > 0:
            this_round_of_descendants = non_complete_descendants.values()

            for d in this_round_of_descendants:
                descendants_to_union = set()
                for component_id in d["descendants"]:
                    if component_id in descendants_dict:
                        component_descendants = descendants_dict[component_id]["descendants"]
                    else:
                        component_descendants = set()
                    descendants_to_union |= component_descendants
                if len(descendants_to_union - d["descendants"]) == 0:
                    del non_complete_descendants[d["id"]]
                    points = self.uow.component_points.get_master_points_by_component_ids(map(lambda desc: [desc, True], list(d["descendants"])))
                    for p in points:
                        point_mappings.append({'component_id': d['id'], 'master_point_num': p["component_point_num"]})
                else:
                    d["descendants"] |= descendants_to_union
            pass_counter += 1
            print "Pass " + str(pass_counter) + " complete"
            print str(len(non_complete_descendants)) + " components remaining"

        print "Convert descendants to flat list..."

        flat_list = []
        for g in descendants:
            for d in g["descendants"]:
                flat_list.append({"component_id": g["id"], "descendant_component_id": d})

        print "Begin inserting flat list records..."

        num_flat_list = len(flat_list)
        for x in range(0, num_flat_list, 2000):
            batch = flat_list[x:(x + 2000)]
            try:
                self.uow.components.insert_flat_components(batch)
            except Exception as e:
                print("error")
                raise
            print "Inserted " + str(x + len(batch)) + "/" + str(num_flat_list) + " components/descendant relationships"

        for x in range(0, len(point_mappings), 2000):
            batch = point_mappings[x:(x + 2000)]
            try:
                self.uow.components.insert_component_master_point_mappings(batch)
            except Exception as e:
                print "error"
                raise
            print "Inserted " + str(x + len(batch)) + "/" + str(len(point_mappings)) + " component/master_point mappings"

        print "Finished inserting components records!"


if "__main__" == __name__:
    generator = FlatTableGenerator()
    generator.generate_flat_groups()
    generator.generate_flat_naics_codes()
    generator.generate_flat_sic_codes()
    generator.generate_flat_components()