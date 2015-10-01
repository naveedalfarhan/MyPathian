__author__ = 'badams'


class UnmappedSyrxNumRepository():
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.unmapped_syrx_nums

    def get_all(self):
        return self.uow.run_list(self.table)

    def get_by_syrx_num(self, syrx_num):
        return self.uow.run_list(self.table.get_all(syrx_num, index='syrx_num'))

    def add_syrx_num(self, syrx_num):
        exists = self.get_by_syrx_num(syrx_num['syrx_num'])
        if len(exists) < 1:
            self.uow.run(self.table.insert(syrx_num))

    def remove_syrx_num(self, syrx_num):
        self.uow.run(self.table.get_all(syrx_num, index="syrx_num").delete())