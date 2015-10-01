class SicRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.sic_codes
        self.flat_table = uow.tables.flat_sic_codes
        self.mapping_table = uow.tables.sic_groups_mapping
        self.groups_table = uow.tables.groups

    def get_children_of(self, sic_code):
        if sic_code:
            cursor = self.uow.run(self.table
                                  .get_all(sic_code, index="parent_code")
                                  .map(lambda code: {"id": code['code'], "name": code['name']})
                                  .order_by("id"))
        else:
            cursor = self.uow.run(self.table
                                  .order_by("code")
                                  .filter({'parent_code': None})
                                  .map(lambda code: {"id": code['code'], "name": code['name']}))

        children = []
        for c in cursor:
            c['childIds'] = self.uow.run_list(self.table
                                                 .get_all(c['id'], index="parent_code")
                                                 .map(lambda code: {"id": code['code'], "name": code['name']})
                                                 .order_by("id"))
            # get groups child ids if there are any groups for the sic code
            c['childIds'] += self.uow.run_list(self.groups_table.get_all(c['id'], index='sic_code'))
            children.append(c)

        return children

    def get_all(self, sic_codes=None):
        if sic_codes is None:
            sic_list = self.uow.run_list(self.table)
            return sic_list
        sic_list = self.uow.run_list(self.table.get_all(*sic_codes, index='code'))
        sic_dict = dict((n["code"], n["description"]) for n in sic_list)
        return sic_dict

    def get_level_two(self):
        sic_list = self.uow.run_list(self.table
                                     .between(100, 10000, index="numeric_code")
                                     .order_by(index="numeric_code"))
        return sic_list

    def get_by_code(self, sic_code):
        raw = self.uow.run_list(self.table.get_all(sic_code, index='code'))[0]
        return raw

    def get_descendants(self, code):
        descendants = set(self.uow.run_list(self.flat_table
                                            .get_all(code, index='code')
                                            .map(lambda record: record['descendant'])))
        return descendants

    def get_group_descendants(self, sic_code):
        groups = self.uow.run_list(self.mapping_table
                                   .get_all(sic_code, index='code')
                                   .map(lambda record: record['group_descendant']))
        return groups

    def get_by_parent(self, parent_code):
        data = self.uow.run_list(self.table.filter({"parent_code": parent_code}))
        return data

    def delete_all(self):
        self.uow.run(self.table.delete())

    def insert_batch(self, records):
        self.uow.run(self.table.insert(records))

    def insert_into_flat_sic(self, records):
        self.uow.run(self.flat_table.insert(records))

    def insert_into_mapping_table(self, records):
        self.uow.run(self.mapping_table.insert(records))

    def delete_flat_table(self):
        self.uow.run(self.flat_table.delete())
        self.uow.run(self.mapping_table.delete())