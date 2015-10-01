from datetime import datetime
import rethinkdb as r


class CompiledPointRecordRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = self.uow.tables.compiled_equipment_point_records

    def get_compiled_point_data(self, point_nums, report_year, comparison_type, demand_type):
        if demand_type in ["peak", "offpeak"]:
            data = self.get_demand_compiled_point_data(point_nums, report_year, comparison_type, demand_type)
        else:
            data = self.get_all_compiled_point_data(point_nums, report_year, comparison_type)

        return self.format_for_kendo(data)

    @staticmethod
    def point_num_value_group_func(x):
        return {"point_num": x['point_num'], "comparison_value": x["comparison_value"]}

    @staticmethod
    def mapping_func(x):
        return {"sum_value": x['sum_value'], "sum_hours_in_record": x["sum_hours_in_record"]}

    @staticmethod
    def reduce_func(a, b):
        return {"sum_value": a['sum_value'] + b['sum_value'],
                "sum_hours_in_record": a['sum_hours_in_record'] + b['sum_hours_in_record']}

    @staticmethod
    def final_mapping_func(x):
        return {"point_num": x['group']['point_num'],
                'sum_value': x['reduction']['sum_value'],
                'sum_hours_in_record': x['reduction']['sum_hours_in_record'],
                'comparison_value': x['group']['comparison_value']}

    @staticmethod
    def point_num_group_func(x):
        return {"point_num": x['point_num']}

    def get_all_compiled_point_data(self, point_nums, report_year, comparison_type):
        index_list = [[point_num, comparison_type, report_year] for point_num in point_nums]

        rv = self.uow.run_list(self.table.get_all(*index_list, index="point_no_peak")
                               .group(self.point_num_value_group_func)
                               .map(self.mapping_func)
                               .reduce(self.reduce_func)
                               .ungroup()
                               .map(self.final_mapping_func)
                               .group(self.point_num_group_func)
                               .ungroup())

        return rv

    def get_demand_compiled_point_data(self, point_nums, report_year, comparison_type, demand_type):
        index_list = [[point_num, comparison_type, report_year, demand_type] for point_num in point_nums]

        rv = self.uow.run_list(self.table.get_all(*index_list, index="point_has_peak")
                               .group(self.point_num_value_group_func)
                               .map(self.mapping_func)
                               .reduce(self.reduce_func)
                               .ungroup()
                               .map(self.final_mapping_func)
                               .group(self.point_num_group_func)
                               .ungroup())

        return rv

    @staticmethod
    def format_for_kendo(data):
        final_data = [{'name': obj['group']['point_num'],
                       'data': [[x['comparison_value'], x['sum_value']] for x in obj['reduction']]} for obj in data]
        return final_data

    @staticmethod
    def syrx_group_func(x):
        return {
            'comparison_value': x['comparison_value']
        }

    @staticmethod
    def syrx_map_func(x):
        return {
            'sum_value': x['sum_value'],
            'sum_hours_in_record': x['sum_hours_in_record']
        }

    @staticmethod
    def syrx_reduce_func(a, b):
        return {
            'sum_value': a['sum_value'] + b['sum_value'],
            'sum_hours_in_record': a['sum_hours_in_record'] + b['sum_hours_in_record']
        }

    @staticmethod
    def syrx_final_map_func(x):
        return {
            'comparison_value': x['group']['comparison_value'],
            'sum_value': x['reduction']['sum_value'],
            'sum_hours_in_record': x['reduction']['sum_hours_in_record']
        }

    @staticmethod
    def format_syrx_data_for_kendo(data):
        final_data = [{'name': '',
                       'data': [[x['comparison_value'], round(x['sum_value'] /
                                                              (x['sum_hours_in_record'] * 1.0 / 0.25), 5)] for x in data]}]
        return final_data

    def get_data_for_syrx_nums(self, syrx_nums, report_year, start_month, end_month):
        index_list = [[num, report_year, 'temp'] for num in syrx_nums]
        if len(index_list) < 1:
            return []
        rv = self.uow.run_list(self.table.get_all(*index_list, index='syrx_year')
                               .filter((r.row['month'] >= start_month) & (r.row['month'] <= end_month))
                               .group(self.syrx_group_func)
                               .map(self.syrx_map_func)
                               .reduce(self.syrx_reduce_func)
                               .ungroup()
                               .map(self.syrx_final_map_func))
        return self.format_syrx_data_for_kendo(rv)

    @staticmethod
    def summation_map_func(x):
        return {
            'sum_value': x['sum_value']
        }

    @staticmethod
    def summation_reduce_func(a,b):
        return {
            'sum_value': a['sum_value'] + b['sum_value']
        }

    @staticmethod
    def default_func():
        return {
            'sum_value': 0
        }

    def get_year_consumption_data_for_points(self, equipment_points, year):
        index_list = [[point['syrx_num'], year, 'temp'] for point in equipment_points]
        if len(index_list) < 1:
            return []
        rv = self.uow.run(self.table.get_all(*index_list, index='syrx_year')
                          .map(self.summation_map_func)
                          .reduce(self.summation_reduce_func)
                          .default(self.default_func))
        return rv

    def get_month_consumption_data_for_points(self, equipment_points, year):
        index_list = [[point['syrx_num'], year, 'temp'] for point in equipment_points]
        if len(index_list) < 1:
            return []
        rv = self.uow.run(self.table.get_all(*index_list, index='syrx_year')
                          .filter({'month':datetime.now().month})
                          .map(self.summation_map_func)
                          .reduce(self.summation_reduce_func)
                          .default(self.default_func))
        return rv

    def records_exist_for_get_all(self, indexes, index_name):
        count = self.uow.run(self.table.get_all(*indexes, index=index_name).count())
        return count > 0

    @staticmethod
    def ppsn_map_func(record):
        return {'sum_value': record['sum_value'],
                'sum_hours_in_record': record['sum_hours_in_record']}

    @staticmethod
    def ppsn_reduce_func(a, b):
        return {'sum_value': a['sum_value'] + b['sum_value'],
                'sum_hours_in_record': a['sum_hours_in_record'] + b['sum_hours_in_record']}

    def get_ppsn(self, syrx_nums, report_year):
        indexes = [[num, report_year, 'temp'] for num in syrx_nums]
        if len(indexes) < 1:
            return {'ppsn': 0, 'sum_hours_in_record': 0, 'sum_value': 0}

        # make sure data exists
        data_exists = self.records_exist_for_get_all(indexes, 'syrx_year')
        if not data_exists:
            return {'ppsn': 0, 'sum_hours_in_record': 0, 'sum_value': 0}

        rv = self.uow.run(self.table.get_all(*indexes, index='syrx_year')
                          .map(self.ppsn_map_func)
                          .reduce(self.ppsn_reduce_func))

        # if there is only one record the reduce step will not run
        if 'ppsn' not in rv and 'sum_hours_in_record' in rv and 'sum_value' in rv:
            rv['ppsn'] = rv['sum_value'] * 1.0 / rv['sum_hours_in_record']

        # if there is nothing then return a dict with 0's
        if 'ppsn' not in rv or 'sum_hours_in_record' not in rv or 'sum_value' not in rv:
            rv = {'ppsn': 0, 'sum_hours_in_record': 0, 'sum_value': 0}
        return rv

    def delete_for_syrx_num(self, syrx_num):
        self.uow.run(self.table.get_all(syrx_num, index='syrx_num').delete())
