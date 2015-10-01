__author__ = 'badams'


class UnmappedVendorPointRecordRepository():
    def __init__(self, uow):
        self.uow = uow
        self.table = self.uow.tables.unmapped_vendor_point_records

    def insert_unmapped_vendor_point_records(self, unmapped_vendor_point_records):
        self.uow.run(self.table.insert(unmapped_vendor_point_records))

    def get_all_vendor_points(self):
        return self.uow.run_list(self.table.pluck('vendor_point').distinct())

    def get_all_vendor_point_records_for_johnson(self, vendor_point):
        return self.uow.run_list(self.table.get_all([vendor_point['johnson_fqr'], vendor_point['johnson_site_id']], index='johnson'))

    def get_all_vendor_point_records_for_fieldserver(self, vendor_point):
        return self.uow.run_list(self.table.get_all([vendor_point['fieldserver_offset'], vendor_point['fieldserver_site_id']], index='fieldserver'))

    def get_all_vendor_point_records_for_invensys(self, vendor_point):
        return self.uow.run_list(self.table.get_all([vendor_point['invensys_point_name'], vendor_point['invensys_equipment_name'], vendor_point['invensys_site_name']], index='invensys'))

    def get_all_vendor_point_records_for_siemens(self, vendor_point):
        return self.uow.run_list(self.table.get_all([vendor_point['siemens_meter_name']], index='siemens'))

    def delete_all_for_johnson_point(self, vendor_point):
        self.uow.run(self.table.get_all([vendor_point['johnson_fqr'], vendor_point['johnson_site_id']], index='johnson').delete())

    def delete_all_for_fieldserver_point(self, vendor_point):
        self.uow.run(self.table.get_all([vendor_point['fieldserver_offset'], vendor_point['fieldserver_site_id']], index='fieldserver').delete())

    def delete_all_for_invensys_point(self, vendor_point):
        self.uow.run(self.table.get_all([vendor_point['invensys_point_name'], vendor_point['invensys_equipment_name'], vendor_point['invensys_site_name']], index='invensys').delete())

    def delete_all_for_siemens_point(self, vendor_point):
        self.uow.run(self.table.get_all([vendor_point['siemens_meter_name']], index='siemens').delete())