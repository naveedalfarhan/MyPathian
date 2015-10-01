from compile_energy_records import EnergyRecordCompiler
from db.uow import UoW

__author__ = 'badams'


class UnmappedSyrxNumHandler():
    def __init__(self):
        self.uow = UoW(False)
        self.logger = None
        self.unmapped_syrx_nums = None

    def run(self):
        # find all of the syrx numbers that have been unmapped
        self.logger.debug('Finding all unmapped syrx numbers...')
        self._get_unmapped_syrx_nums()

        # loop through syrx numbers and move their data to a table to hold it
        self.logger.debug('Moving records for unmapped syrx numbers...')
        self._move_data_for_syrx_nums()

        # remove non-compiled records for the syrx number
        self.logger.debug('Deleting non-compiled records for unmapped syrx numbers...')
        self._delete_noncompiled_records_for_syrx_nums()

        # remove the compiled records for the syrx number
        self.logger.debug('Deleting compiled records for unmapped syrx numbers...')
        self._delete_compiled_records_for_syrx_nums()

        # if there are new mappings, see if they are mapped to a vendor point in the unknown table
        self.logger.debug('Finding all previously unmapped records for new mappings...')
        self._move_data_to_new_mappings()

    def _get_unmapped_syrx_nums(self):
        # unmapped_syrx_nums are a dictionary of {'syrx_num': String, 'vendor_point': Dictionary}
        self.unmapped_syrx_nums = self.uow.unmapped_syrx_nums.get_all()

    def _move_data_for_syrx_nums(self):
        for unmapped_syrx_num in self.unmapped_syrx_nums:
            self._move_data_for_syrx_num(unmapped_syrx_num)

            # remove from unmapped syrx num table
            self.uow.unmapped_syrx_nums.remove_syrx_num(unmapped_syrx_num['syrx_num'])

    def _move_data_for_syrx_num(self, unmapped_syrx_num):
        # check if it was previously global by checking length of records in global_vendor_point_records for point
        vendor_point = unmapped_syrx_num['vendor_point']
        source = unmapped_syrx_num['vendor_point']['source']
        global_records = []
        mappings = []
        if source == "johnson":
            global_records = self.uow.global_vendor_point_records.get_all_for_johnson_point(vendor_point['johnson_site_id'],
                                                                                            vendor_point['johnson_fqr'])
            mappings = self.uow.data_mapping.get_mappings_for_johnson_site_id_fqr([[vendor_point['johnson_site_id'],
                                                                                    vendor_point['johnson_fqr']]])
        elif source == "fieldserver":
            global_records = self.uow.global_vendor_point_records.get_all_for_fieldserver_point(vendor_point['fieldserver_site_id'],
                                                                                                vendor_point['fieldserver_offset'])
            mappings = self.uow.data_mapping.get_mappings_for_fieldserver_site_id_offset([[vendor_point['fieldserver_site_id'],
                                                                                           vendor_point['fieldserver_offset']]])
        elif source == "invensys":
            global_records = self.uow.global_vendor_point_records.get_all_for_invensys_point(vendor_point['invensys_site_name'],
                                                                                             vendor_point['invensys_equipment_name'],
                                                                                             vendor_point['invensys_point_name'])
            mappings = self.uow.data_mapping.get_mappings_for_invensys_site_equipment_point([[vendor_point['invensys_site_name'],
                                                                                              vendor_point['invensys_equipment_name'],
                                                                                              vendor_point['invensys_point_name']]])
        elif source == "siemens":
            global_records = self.uow.global_vendor_point_records.get_all_for_siemens_point(vendor_point['siemens_meter_name'])
            mappings = self.uow.data_mapping.get_mappings_for_siemens_meter_name([[vendor_point['siemens_meter_name']]])

        if len(global_records) > 0 and len(list(mappings)) <= 1:  # previously global
            self._handle_unmapping_records_for_global_vendor_point(unmapped_syrx_num, global_records)
            # remove from global_vendor_point_records
            if source == "johnson":
                self.uow.global_vendor_point_records.delete_all_for_johnson_point(vendor_point['johnson_site_id'],
                                                                                  vendor_point['johnson_fqr'])
            elif source == "fieldserver":
                self.uow.global_vendor_point_records.delete_all_for_fieldserver_point(vendor_point['fieldserver_site_id'],
                                                                                      vendor_point['fieldserver_offset'])
            elif source == "invensys":
                self.uow.global_vendor_point_records.delete_all_for_invensys_point(vendor_point['invensys_site_name'],
                                                                                   vendor_point['invensys_equipment_name'],
                                                                                   vendor_point['invensys_point_name'])
            elif source == "siemens":
                self.uow.global_vendor_point_records.delete_all_for_siemens_point(vendor_point['siemens_meter_name'])

        else:
            records = self.uow.equipment.get_data_for_syrx_num(unmapped_syrx_num['syrx_num'])
            self._handle_unmapping_records_for_syrx_num(unmapped_syrx_num, records)

    def _handle_unmapping_records_for_syrx_num(self, syrx_num, records):
        """
        Changes the data properly and moves the records to the unmapped_vendor_data_table
        :param syrx_num: the current unmapped_syrx_num of the data
        :param records: the list of records
        :return:
        """
        data = []
        for record in records:
            del record['syrx_num']
            del record['id']
            record.update(syrx_num['vendor_point'])
            data.append(record)

        self.uow.unmapped_vendor_point_records.insert_unmapped_vendor_point_records(data)

    def _handle_unmapping_records_for_global_vendor_point(self, unmapped_syrx_num, global_records):
        """
        Changes the data properly and moves the records to the unmapped vendor_data_table
        :param unmapped_syrx_num: the current unmapped_syrx_num of the data
        :param global_records: the list of global records
        :return:
        """
        data = []
        for record in global_records:
            del record['id']
            data.append(record)

        self.uow.unmapped_vendor_point_records.insert_unmapped_vendor_point_records(data)


    def _delete_compiled_records_for_syrx_nums(self):
        for syrx_num in self.unmapped_syrx_nums:
            self.uow.compiled_point_records.delete_for_syrx_num(syrx_num['syrx_num'])

    def _move_data_to_new_mappings(self):
        self.logger.debug('Moving data for johnson mappings...')
        self._move_unknown_data_for_johnson()
        self.logger.debug('Moving data for fieldserver mappings...')
        self._move_unknown_data_for_fieldserver()
        self.logger.debug('Moving data for invensys mappings...')
        self._move_unknown_data_for_invensys()
        self.logger.debug('Moving data for siemens mappings...')
        self._move_unknown_data_for_siemens()

    def _move_unknown_data_for_johnson(self):
        data_mappings = self.uow.data_mapping.get_all_mappings_for_johnson()
        for data_mapping in data_mappings:
            # format the vendor point mapping in such a form that the index will recognize it
            mapping = {'johnson_fqr': data_mapping['johnson_fqr'],
                       'johnson_site_id': data_mapping['johnson_site_id'],
                       'source': 'johnson'}
            if 'global' in data_mapping and data_mapping['global'] is True:
                self._move_to_global_vendor_records(mapping, 'johnson')
            else:
                self._add_data_for_mapping(mapping, data_mapping['syrx_num'])

    def _move_unknown_data_for_fieldserver(self):
        data_mappings = self.uow.data_mapping.get_all_mappings_for_fieldserver()
        for data_mapping in data_mappings:
            # format the vendor point mapping in such a form that the index will recognize it
            mapping = {'fieldserver_offset': data_mapping['fieldserver_offset'],
                       'fieldserver_site_id': data_mapping['fieldserver_site_id'],
                       'source': 'fieldserver'}
            if 'global' in data_mapping and data_mapping['global'] is True:
                self._move_to_global_vendor_records(mapping, 'fieldserver')
            else:
                self._add_data_for_mapping(mapping, data_mapping['syrx_num'])

    def _move_unknown_data_for_invensys(self):
        data_mappings = self.uow.data_mapping.get_all_mappings_for_invensys()
        for data_mapping in data_mappings:
            # format the vendor point mapping in such a form that the index will recognize it
            mapping = {'invensys_point_name': data_mapping['invensys_point_name'],
                       'invensys_equipment_name': data_mapping['invensys_equipment_name'],
                       'invensys_site_name': data_mapping['invensys_site_name'],
                       'source': 'invensys'}
            if 'global' in data_mapping and data_mapping['global'] is True:
                self._move_to_global_vendor_records(mapping, 'invensys')
            else:
                self._add_data_for_mapping(mapping, data_mapping['syrx_num'])

    def _move_unknown_data_for_siemens(self):
        data_mappings = self.uow.data_mapping.get_all_mappings_for_siemens()
        for data_mapping in data_mappings:
            # format the vendor point mapping in such a form that the index will recognize it
            mapping = {'siemens_meter_name': data_mapping['siemens_meter_name'],
                       'source': 'siemens'}
            if 'global' in data_mapping and data_mapping['global'] is True:
                self._move_to_global_vendor_records(mapping, 'siemens')
            else:
                self._add_data_for_mapping(mapping, data_mapping['syrx_num'])

    def _add_data_for_mapping(self, mapping, syrx_num):
        if mapping['source'] == 'johnson':
            vendor_point_records = self.uow.unmapped_vendor_point_records.get_all_vendor_point_records_for_johnson(mapping)
        elif mapping['source'] == 'fieldserver':
            vendor_point_records = self.uow.unmapped_vendor_point_records.get_all_vendor_point_records_for_fieldserver(mapping)
        elif mapping['source'] == 'invensys':
            vendor_point_records = self.uow.unmapped_vendor_point_records.get_all_vendor_point_records_for_invensys(mapping)
        else:
            vendor_point_records = self.uow.unmapped_vendor_point_records.get_all_vendor_point_records_for_siemens(mapping)
        insert_list = []
        if len(vendor_point_records) < 1:
            return

        for record in vendor_point_records:
            record['syrx_num'] = syrx_num
            if mapping['source'] == 'johnson':
                del record['johnson_fqr']
                del record['johnson_site_id']
            elif mapping['source'] == 'fieldserver':
                del record['fieldserver_offset']
                del record['fieldserver_site_id']
            elif mapping['source'] == 'invensys':
                del record['invensys_point_name']
                del record['invensys_equipment_name']
                del record['invensys_site_name']
            else:
                del record['siemens_meter_name']

            del record['source']
            del record['id']
            insert_list.append(record)

        date_list = [r['date'] for r in insert_list]

        min_date = min(date_list)
        max_date = max(date_list)

        self.uow.energy_records.insert_equipment_point_records(insert_list)
        energy_record_compiler = EnergyRecordCompiler()
        energy_record_compiler.compile_component_point_records_by_year_span(syrx_num, min_date, max_date)
        if mapping['source'] == 'johnson':
            self.uow.unmapped_vendor_point_records.delete_all_for_johnson_point(mapping)
        elif mapping['source'] == 'fieldserver':
            self.uow.unmapped_vendor_point_records.delete_all_for_fieldserver_point(mapping)
        elif mapping['source'] == 'invensys':
            self.uow.unmapped_vendor_point_records.delete_all_for_invensys_point(mapping)
        else:
            self.uow.unmapped_vendor_point_records.delete_all_for_siemens_point(mapping)

    def _delete_noncompiled_records_for_syrx_nums(self):
        for syrx_num in self.unmapped_syrx_nums:
            self.uow.energy_records.delete_for_syrx_num(syrx_num['syrx_num'])

    def _move_to_global_vendor_records(self, mapping, source):
        if source == 'johnson':
            vendor_point_records = self.uow.unmapped_vendor_point_records.get_all_vendor_point_records_for_johnson(mapping)
        elif source == 'fieldserver':
            vendor_point_records = self.uow.unmapped_vendor_point_records.get_all_vendor_point_records_for_fieldserver(mapping)
        elif source == 'invensys':
            vendor_point_records = self.uow.unmapped_vendor_point_records.get_all_vendor_point_records_for_invensys(mapping)
        else:
            vendor_point_records = self.uow.unmapped_vendor_point_records.get_all_vendor_point_records_for_siemens(mapping)

        self.uow.global_vendor_point_records.insert_global_vendor_point_records(vendor_point_records)

        if source == 'johnson':
            self.uow.unmapped_vendor_point_records.delete_all_for_johnson_point(mapping)
        elif source == 'fieldserver':
            self.uow.unmapped_vendor_point_records.delete_all_for_fieldserver_point(mapping)
        elif source == 'invensys':
            self.uow.unmapped_vendor_point_records.delete_all_for_invensys_point(mapping)
        else:
            self.uow.unmapped_vendor_point_records.delete_all_for_siemens_point(mapping)