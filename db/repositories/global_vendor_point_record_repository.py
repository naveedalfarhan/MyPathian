__author__ = 'Brian'


class GlobalVendorPointRecordRepository():
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.global_vendor_point_records

    def insert_global_vendor_point_records(self, records):
        self.uow.run(self.table.insert(records))

    def get_all_for_johnson_point(self, johnson_site_id, johnson_fqr):
        return self.uow.run_list(self.table.get_all([johnson_site_id, johnson_fqr], index='johnson'))

    def get_all_for_fieldserver_point(self, fieldserver_site_id, fieldserver_offset):
        return self.uow.run_list(self.table.get_all([fieldserver_site_id, fieldserver_offset], index='fieldserver'))

    def get_all_for_invensys_point(self, invensys_site_name, invensys_equipment_name, invensys_point_name):
        return self.uow.run_list(self.table.get_all([invensys_site_name, invensys_equipment_name, invensys_point_name],
                                                    index='invensys'))

    def get_all_for_siemens_point(self, siemens_meter_name):
        return self.uow.run_list(self.table.get_all([siemens_meter_name], index='siemens'))

    @staticmethod
    def date_map_func(x):
        return x['date']

    def get_existing_dates_for_johnson(self, site_id, fqr):
        return self.uow.run_list(self.table.get_all([site_id, fqr], index='johnson')
                                 .map(self.date_map_func))

    def get_existing_dates_for_fieldserver(self, site_id, offset):
        return self.uow.run_list(self.table.get_all([site_id, offset], index='fieldserver')
                                 .map(self.date_map_func))

    def get_existing_dates_for_invensys(self, site_name, equipment_name, point_name):
        return self.uow.run_list(self.table.get_all([site_name, equipment_name, point_name], index='invensys')
                                 .map(self.date_map_func))

    def get_existing_dates_for_siemens(self, meter_name):
        return self.uow.run_list(self.table.get_all([meter_name], index='siemens')
                                 .map(self.date_map_func))

    def delete_all_for_johnson_point(self, site_id, fqr):
        self.uow.run(self.table.get_all([site_id, fqr], index='johnson').delete())

    def delete_all_for_fieldserver_point(self, site_id, offset):
        self.uow.run(self.table.get_all([site_id, offset], index='fieldserver').delete())

    def delete_all_for_invensys_point(self, site_name, equipment_name, point_name):
        self.uow.run(self.table.get_all([site_name, equipment_name, point_name], index='invensys').delete())

    def delete_all_for_siemens_point(self, meter_name):
        self.uow.run(self.table.get_all([meter_name], index='siemens').delete())