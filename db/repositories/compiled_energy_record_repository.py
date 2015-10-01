import rethinkdb as r

class CompiledEnergyRecordRepository:
    def __init__(self, uow):
        self.uow = uow
        self.compiled_energy_records_table = uow.tables.compiled_energy_records
        self.energy_records_table = uow.tables.energyrecords
        self.compiled_equipment_point_records_table = uow.tables.compiled_equipment_point_records
        self.equipment_point_records_table = uow.tables.equipment_point_records

    """
    get all records, group by account, year, comparison_value, month, type, and peak
    sum btus, (kvar, kwh or mcf), size normalization, price normalization, and hours
    """
    def get_compiled_energy_records(self, account_type, comparison_type, start_year=None, end_year=None,
                                    start_date=None, end_date=None,
                                    account_id=None):
        if account_type == "electric":
            map_lambda = lambda r: {'btu': r['energy']['btu'], 'kvar': r['energy']['kvar'], 'kwh': r['energy']['kwh'],
                                    'size_normalization': r['size_normalization'] * r['hours_in_record'],
                                    'price_normalization': r['price_normalization'] * r['hours_in_record'],
                                    'hrs': r['hours_in_record']}

            reduce_lambda = lambda a, b: {'btu': a['btu'] + b['btu'],
                                          'kvar': a['kvar'] + b['kvar'],
                                          'kwh': a['kwh'] + b['kwh'],
                                          'size_normalization': a['size_normalization'] + b['size_normalization'],
                                          'price_normalization': a['price_normalization'] + b['price_normalization'],
                                          'hrs': a['hrs'] + b['hrs']}

        elif account_type == "gas":
            map_lambda = lambda r: {'btu': r['energy']['btu'], 'mcf': r['energy']['mcf'],
                                    'size_normalization': r['size_normalization'] * r['hours_in_record'],
                                    'price_normalization': r['price_normalization'] * r['hours_in_record'],
                                    'hrs': r['hours_in_record']}

            reduce_lambda = lambda a, b: {'btu': a['btu'] + b['btu'],
                                          'mcf': a['mcf'] + b['mcf'],
                                          'size_normalization': a['size_normalization'] + b['size_normalization'],
                                          'price_normalization': a['price_normalization'] + b['price_normalization'],
                                          'hrs': a['hrs'] + b['hrs']}

        else:
            map_lambda = lambda r: {'btu': r['energy']['btu'],
                                    'size_normalization': r['size_normalization'] * r['hours_in_record'],
                                    'price_normalization': r['price_normalization'] * r['hours_in_record'],
                                    'hrs': r['hours_in_record']}

            reduce_lambda = lambda a, b: {'btu': a['btu'] + b['btu'],
                                          'size_normalization': a['size_normalization'] + b['size_normalization'],
                                          'price_normalization': a['price_normalization'] + b['price_normalization'],
                                          'hrs': a['hrs'] + b['hrs']}

        q = self.energy_records_table
        if account_id:
            q = q.get_all(account_id, index="account_id")
        elif account_type:
            q = q.get_all(account_type, index='type')

        q = (q.group(lambda record: {'account_id': record['account_id'],
                                     'year': record['local_year'],
                                     'comparison_value': record['weather'][comparison_type],
                                     'month': record['local_month'],
                                     'type': record["type"],
                                     'peak': record['peak']})
             .map(map_lambda)
             .reduce(reduce_lambda)
             .ungroup())

        if start_year and end_year:
            q = q.filter(r.row["group"]["year"].le(end_year) and r.row["group"]["year"].ge(start_year))
        elif start_date and end_date:
            q = q.filter(r.row['group']['month'].ge(start_date.month) & r.row['group']['month'].le(end_date.month) &
                         r.row['group']['year'].ge(start_date.year) & r.row['group']['year'].le(end_date.year))


        data = self.uow.run_list(q)
        return data

    def get_compiled_component_point_records(self, comparison_type, syrx_num=None, start_date=None, end_date=None):
        q = self.equipment_point_records_table
        if syrx_num is not None:
            q = q.get_all(syrx_num, index="syrx_num")
        if start_date and end_date:
            q = q.filter(r.row['local_month'].ge(start_date.month) & r.row['local_month'].le(end_date.month) &
                         r.row['local_year'].ge(start_date.year) & r.row['local_year'].le(end_date.year))

        data = self.uow.run_list(q
                                 .group(lambda x: {'syrx_num': x['syrx_num'], 'year': x['local_year'],
                                                   'comparison_value': x['weather'][comparison_type],
                                                   'month': x['local_month'], 'peak': x['peak']})
                                 .map(lambda record: {'value': record['value'], 'hrs': record['hours_in_record']})
                                 .reduce(lambda a, b: {'value': a['value'] + b['value'], 'hrs': a['hrs'] + b['hrs']})
                                 .ungroup())

        return data

    def insert_compiled_energy_records(self, records):
        self.uow.run(self.compiled_energy_records_table.insert(records))

    def insert_compiled_equipment_point_records(self, records):
        self.uow.run(self.compiled_equipment_point_records_table.insert(records))

    """
    index_entries is a list of lists. each list should have three elements - the point syrx number, the comparison
    type, and the year. returned will be aggregates of the compiled records, grouped by year and comparison value.
    if consider_demand_type is true, then each list should have four elements, the fourth being the demand type.
    """
    def get_compiled_equipment_point_records(self, index_entries, consider_demand_type=False):
        index_name = "no_peak"
        if consider_demand_type:
            index_name = "has_peak"
        records = self.uow.run_list(self.compiled_equipment_point_records_table
                                    .get_all(*index_entries, index=index_name)
                                    .group(lambda record: {"year": record['year'],
                                                           "comparison_value": record["comparison_value"]})
                                    .map(lambda record: {"sum_value": record["sum_value"],
                                                         "sum_hours_in_record": record["sum_hours_in_record"]})
                                    .reduce(lambda a, b: {"sum_value": a["sum_value"] + b["sum_value"],
                                                          "sum_hours_in_record": a["sum_hours_in_record"] + b["sum_hours_in_record"]})
                                    .ungroup())
        return records

    """
    index_entries is a list of lists. each list should have three or four elements - the account id, the comparison
    type, the year, and the demand type (optional). returned will be aggregates of the compiled records, grouped by year
    and comparison value. if consider_demand_type is true, then each list should have four elements, the fourth being
    the demand type.

    group_by_account and group_by_month should never both be set to True. If they both are set to True, it will be grouped
    by account.
    """
    def get_compiled_energy_records_for_report(self, index_entries, data_field_name=None, consider_demand_type=False,
                                               group_by_account=False, group_by_month=None):

        # make sure index_entries is not empty
        if len(index_entries) < 1:
            return []

        index_name = "no_peak"
        if consider_demand_type:
            index_name = "has_peak"

        if group_by_account and group_by_month:
            group_func = lambda x: {"year": x['year'], "value": x["comparison_value"], "account_id": x["account_id"], "month": x["month"]}
        elif group_by_account:
            group_func = lambda x: {"year": x['year'], "value": x["comparison_value"], "account_id": x["account_id"]}
        elif group_by_month:
            group_func = lambda x: {"year": x['year'], "month": x['month'], "value": x["comparison_value"]}
        else:
            group_func = lambda x: {"year": x['year'], "value": x["comparison_value"]}

        if data_field_name:
            map_func = lambda x: {data_field_name: x[data_field_name],
                                 "sum_btu": x["sum_btu"],
                                 "sum_size_normalization": x["sum_size_normalization"],
                                 "sum_price_normalization": x["sum_price_normalization"],
                                  "sum_hours_in_record": x["sum_hours_in_record"]}
            reduce_func = lambda a, b: {data_field_name: a[data_field_name] + b[data_field_name],
                                        "sum_btu": a["sum_btu"] + b["sum_btu"],
                                           "sum_size_normalization": a["sum_size_normalization"] + b["sum_size_normalization"],
                                           "sum_price_normalization": a["sum_price_normalization"] + b["sum_price_normalization"],
                                        "sum_hours_in_record": a["sum_hours_in_record"] + b["sum_hours_in_record"]}
        else:
            map_func = lambda x: {"sum_btu": x["sum_btu"],
                                     "sum_size_normalization": x["sum_size_normalization"],
                                     "sum_price_normalization": x["sum_price_normalization"],
                                  "sum_hours_in_record": x["sum_hours_in_record"]}
            reduce_func = lambda a, b: {"sum_btu": a["sum_btu"] + b["sum_btu"],
                                           "sum_size_normalization": a["sum_size_normalization"] + b["sum_size_normalization"],
                                           "sum_price_normalization": a["sum_price_normalization"] + b["sum_price_normalization"],
                                        "sum_hours_in_record": a["sum_hours_in_record"] + b["sum_hours_in_record"]}

        records = self.uow.run_list(self.compiled_energy_records_table
                                    .get_all(*index_entries, index=index_name)
                                    .group(group_func)
                                    .map(map_func)
                                    .reduce(reduce_func)
                                    .ungroup())
        return records

    """
    index_values is a list of lists. each list contains the account id, the comparison type, the year,
    and if consider_demand_type is true, the demand type.
    """
    def get_shared_records_for_report(self, index_values, consider_demand_type=False):
        if consider_demand_type:
            report_index = "has_peak"
        else:
            report_index = "no_peak"

        data = self.uow.run_list(
            self.compiled_energy_records_table
            .get_all(*index_values, index=report_index)
            .inner_join(self.compiled_energy_records_table,
                        lambda arow, brow: r.expr(arow['comparison_value'] == brow['comparison_value'])
                        .and_(arow['comparison_type'] == 'temp').and_(brow['comparison_type'] == 'temp')
                        .and_(arow['year'] != brow['year']))
            .zip()
            .group(lambda record: {'year': record['year'], 'account_id': record['account_id'],
                                   'value': record['comparison_value']})
            .map(lambda record: {'sum_btu': record['sum_btu'],
                                 'p_norm': record['sum_price_normalization'],
                                 's_norm': record['sum_size_normalization'],
                                 'hrs': record['sum_hours_in_record']})
            .reduce(lambda a, b: {'sum_btu': a['sum_btu'] + b['sum_btu'],
                                  'p_norm': a['p_norm'] + b['p_norm'],
                                  's_norm': a['s_norm'] + b['s_norm'],
                                  'hrs': a['hrs'] + b['hrs']})
            .ungroup())

        return data

    """
    index_values is a list of lists. each list contains the account id, the comparison type, the year,
    and if consider_demand_type is true, the demand type.
    """
    def get_independent_records_for_report(self, index_values, year, consider_demand_type=False):
        if consider_demand_type:
            report_index = "has_peak"
        else:
            report_index = "no_peak"

        data = self.uow.run_list(
            self.compiled_energy_records_table
            .get_all(*index_values, index=report_index)
            .group(lambda record: {'year': record['year'], 'account_id': record['account_id'],
                                   'value': record['comparison_value']})
            .map(lambda record: {'sum_btu': record['sum_btu'],
                                'sum_price_normalization': record['sum_price_normalization'],
                                'sum_size_normalization': record['sum_size_normalization'],
                                'hrs': record['sum_hours_in_record']})
            .reduce(lambda a, b: {'sum_btu': a['sum_btu'] + b['sum_btu'],
                                  'sum_price_normalization': a['sum_price_normalization'] + b['sum_price_normalization'],
                                  'sum_size_normalization': a['sum_size_normalization'] + b['sum_size_normalization'],
                                  'hrs': a['hrs'] + b['hrs']})
            .ungroup()
            .filter(r.row['group']['year'] == year))

        return data

    def delete_compiled_records(self, account_id, start_date, end_date):
        self.uow.run(self.compiled_energy_records_table
            .get_all(account_id, index='account_id')
            .filter(r.row['month'].ge(start_date.month) & r.row['month'].le(end_date.month) &
                    r.row['year'].ge(start_date.year) & r.row['year'].le(end_date.year))
            .delete())

    def delete_compiled_equipment_point_records(self, syrx_num, start_date, end_date):
        q = self.compiled_equipment_point_records_table

        # get by syrx number
        q = q.get_all(syrx_num, index="syrx_num")

        # filter by year/month
        q = q.filter(r.row['month'].ge(start_date.month) & r.row['month'].le(end_date.month) &
                     r.row['year'].ge(start_date.year) & r.row['year'].le(end_date.year))

        self.uow.run(q.delete())
    
    def get_accounts_for_group(self, group_id, account_type, report_year, comparison_type, demand_type):
        accounts = []
        if demand_type != 'all':
            if account_type != 'all':
                acc = self.uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
                for a in acc:
                    accounts.append([a['id'], comparison_type, int(report_year), demand_type])
            else:
                for account in self.uow.accounts.get_all_for_group(group_id):
                    accounts.append([account['id'], comparison_type, int(report_year), demand_type])
        else:
            if account_type != 'all':
                acc = self.uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
                for a in acc:
                    accounts.append([a['id'], comparison_type, int(report_year)])
            else:
                for account in self.uow.accounts.get_all_for_group(group_id):
                    accounts.append([account['id'], comparison_type, int(report_year)])
        return accounts
