from collections import defaultdict
import math
from api.models.TotalEnergyData import TotalEnergyData
from db import Db
from AccountRepository import AccountRepository
from GroupRepository import GroupRepository


class CompiledEnergyRepository:
    tablename = "compiled_energy_records"
    r = Db.r
    table = r.db("pathian").table(tablename)

    @classmethod
    def get_intensity_data(cls, group_ids, account_type, report_year, comparison_type, demand_type):
        if demand_type != 'all':
            report_index = "has_peak"
        else:
            report_index = "no_peak"
        y_unit_map = "sum_btu"
        final_data = []
        for group_id in group_ids:
            descendants = GroupRepository.get_descendants(group_id)
            accounts = []
            for g in descendants:
                accounts += cls.get_accounts_for_group(g['id'], account_type, report_year, comparison_type,
                                                   demand_type)

            if len(accounts) >= 1:
                data = Db.r.db("pathian").table("compiled_energy_records").get_all(*accounts, index=report_index).group(
                    lambda record: {"year": record['year'], "value": record["comparison_value"]}).map(
                    lambda record: {y_unit_map: record[y_unit_map],
                                    "sum_size_normalization": record["sum_size_normalization"]}).reduce(
                    lambda a, b: {y_unit_map: a[y_unit_map] + b[y_unit_map],
                                  "sum_size_normalization": a["sum_size_normalization"] + b[
                                      "sum_size_normalization"]}).ungroup().run()
                data_insert = []
                for entry in data:
                    data_insert.append(
                        [entry['group']['value'],
                         entry['reduction'][y_unit_map] / entry['reduction']['sum_size_normalization']])
                final_data.append({'name': GroupRepository.get_group_by_id(group_id).name, 'data': data_insert})
        return final_data

    @classmethod
    def get_accounts_for_group(cls, group_id, account_type, report_year, comparison_type, demand_type):
        accounts = []
        if demand_type != 'all':
            if account_type != 'all':
                acc = AccountRepository.get_by_group_id_and_account_type(group_id, account_type)
                if acc:
                    accounts.append([acc['id'], comparison_type, int(report_year), demand_type])
            else:
                for account in AccountRepository.get_all_for_group(group_id):
                    accounts.append([account['id'], comparison_type, int(report_year), demand_type])
        else:
            if account_type != 'all':
                acc = AccountRepository.get_by_group_id_and_account_type(group_id, account_type)
                if acc:
                    accounts.append([acc['id'], comparison_type, int(report_year)])
            else:
                for account in AccountRepository.get_all_for_group(group_id):
                    accounts.append([account['id'], comparison_type, int(report_year)])
        return accounts

    @classmethod
    def get_total_energy_data_with_y(cls, group_id, report_year, benchmark_year, account_type, comparison_type,  demand_type, y_units, y_unit_map):
        if demand_type != 'all':
            report_index = "has_peak"
        else:
            report_index = "no_peak"

        same_year = int(report_year) == int(benchmark_year)
        unit_factor = get_factor(y_units, y_unit_map)
        data = TotalEnergyData

        descendants = GroupRepository.get_descendants(group_id)
        accounts = []

        # Get all accounts for each group for the desired year
        for g in descendants:
            accounts += cls.get_accounts_for_group(g['id'], account_type, report_year, comparison_type, demand_type)
            if not same_year:
                accounts += cls.get_accounts_for_group(g['id'], account_type, benchmark_year, comparison_type,demand_type)

        if len(accounts) < 1:
            benchmark_data = []
        else:
            benchmark_data = Db.r.db("pathian").table("compiled_energy_records").get_all(*accounts,
                                                                                         index=report_index).group(
                lambda record: {"year": record['year'], "value": record["comparison_value"]}).map(
                lambda record: {y_unit_map: record[y_unit_map],
                                "sum_hours_in_record": record["sum_hours_in_record"]}).reduce(
                lambda a, b: {y_unit_map: a[y_unit_map] + b[y_unit_map],
                              "sum_hours_in_record": a["sum_hours_in_record"] + b["sum_hours_in_record"]}).ungroup().run()

        grouped = defaultdict(list)

        for d in benchmark_data:
            grouped[d['group']['value']].append(d)

        reported_consumption = []
        diff = []
        benchmark_diff = []
        benchmark_consumption = []

        grouped_keys = list(grouped.keys())
        grouped_keys.sort()

        if same_year:
            for value in grouped_keys:
                entry = grouped[value]
                reported_consumption.append(
                    [value, entry[0]['reduction'][y_unit_map] * unit_factor / entry[0]['reduction']['sum_hours_in_record']]
                )
                diff.append([value, 0])
                benchmark_consumption.append(
                    [value, entry[0]['reduction'][y_unit_map] * unit_factor / entry[0]['reduction']['sum_hours_in_record']])
                benchmark_diff.append([value, 0])
        else:
            for value in grouped_keys:
                entry = grouped[value]
                if len(entry) > 1:
                    report_record = 0
                    benchmark_record = 0
                    for record in entry:
                        if record['group']['year'] == int(report_year):
                            report_record = record['reduction'][y_unit_map] * unit_factor / record['reduction'][
                                'sum_hours_in_record']
                            reported_consumption.append([value, report_record])
                        elif record['group']['year'] == int(benchmark_year):
                            benchmark_record = record['reduction'][y_unit_map] * unit_factor / record['reduction'][
                                'sum_hours_in_record']
                            benchmark_consumption.append([value, benchmark_record])
                            benchmark_diff.append([value, 0])

                    diff.append([value, benchmark_record - report_record])

        data.reported_consumption = reported_consumption
        data.benchmark_consumption = benchmark_consumption
        data.diff = diff
        data.benchmark_diff = benchmark_diff
        return data

    @classmethod
    def get_total_energy_data(cls, account, year, benchmark_year, demand_type, y_units, y_unit_map, grouped):
        if demand_type != 'all':
            report_index = "has_peak"
        else:
            report_index = "no_peak"

        same_year = int(year) == int(benchmark_year)
        unit_factor = get_factor(y_units, y_unit_map)
        mmbtu_unit_factor = get_factor('mmbtus', y_unit_map)
        data = TotalEnergyData()

        # change the mapping function to ensure that sum_btu will always be returned from the query
        if y_unit_map.lower() == "sum_btu":
            mapping = lambda record: {'sum_btu': record['sum_btu'], 'sum_hours_in_record': record['sum_hours_in_record'],
                                      'sum_price_normalization': record['sum_price_normalization']}
            reduction = lambda a, b: {'sum_btu': a['sum_btu'] + b['sum_btu'],
                                     "sum_hours_in_record": a["sum_hours_in_record"] + b["sum_hours_in_record"],
                                     'sum_price_normalization': a['sum_price_normalization'] + b['sum_price_normalization']}
        else:
            mapping = lambda record: {'sum_btu': record['sum_btu'], y_unit_map: record[y_unit_map],
                                      'sum_hours_in_record': record['sum_hours_in_record'],
                                      'sum_price_normalization': record['sum_price_normalization']}
            reduction = lambda a, b: {'sum_btu': a['sum_btu'] + b['sum_btu'],
                                     y_unit_map: a[y_unit_map] + b[y_unit_map],
                                     "sum_hours_in_record": a["sum_hours_in_record"] + b["sum_hours_in_record"],
                                     'sum_price_normalization': a['sum_price_normalization'] + b['sum_price_normalization']}

        report_data = Db.r.db("pathian").table("compiled_energy_records").get_all(account, index=report_index).group(
            lambda record: {"year": record['year'], "value": record["comparison_value"]}).map(mapping).reduce(reduction).ungroup().run()

        for d in report_data:
            grouped[d['group']['value']].append(d)

        reported_consumption = []
        diff = []
        benchmark_diff = []
        benchmark_consumption = []

        grouped_keys = list(grouped.keys())
        grouped_keys.sort()

        reported_total = 0
        reported_hours = 0
        benchmark_total = 0
        benchmark_hours = 0
        utility_total = 0

        sum_price_norm = 0
        sum_hours = 0

        if same_year:
            for value in grouped_keys:
                entry = grouped[value]
                reported_consumption.append(
                    [value, entry[0]['reduction'][y_unit_map] * unit_factor / entry[0]['reduction']['sum_hours_in_record']]
                )
                sum_price_norm += entry[0]['reduction']['sum_price_normalization'] * entry[0]['reduction']['sum_hours_in_record']
                sum_hours += entry[0]['reduction']['sum_hours_in_record']

                diff.append([value, 0])
                benchmark_consumption.append(
                    [value, entry[0]['reduction'][y_unit_map] * unit_factor / entry[0]['reduction']['sum_hours_in_record']])
                benchmark_diff.append([value, 0])

                # get totals specifying to convert to mmbtus
                reported_total += entry[0]['reduction']['sum_btu'] * mmbtu_unit_factor / entry[0]['reduction']['sum_hours_in_record']
                benchmark_total += entry[0]['reduction']['sum_btu'] * mmbtu_unit_factor / entry[0]['reduction']['sum_hours_in_record']
                utility_total += entry[0]['reduction']['sum_btu'] * mmbtu_unit_factor / entry[0]['reduction']['sum_hours_in_record']
        else:
            for value in grouped_keys:
                entry = grouped[value]

                # search the entry for the report year and add data to the utility total
                for rec in entry:
                    if rec['group']['year'] == int(year):
                        utility_total += rec['reduction']['sum_btu'] * mmbtu_unit_factor / rec['reduction']['sum_hours_in_record']

                # if the data exists for both years
                if len(entry) > 1:
                    report_record = 0
                    benchmark_record = 0
                    for record in entry:
                        if record['group']['year'] == int(year):
                            report_record = record['reduction'][y_unit_map] * unit_factor / record['reduction'][
                                'sum_hours_in_record']
                            reported_consumption.append([value, report_record])

                            # update totals
                            reported_total += record['reduction']['sum_btu'] * mmbtu_unit_factor / record['reduction'][
                                'sum_hours_in_record']
                            reported_hours += record['reduction']['sum_hours_in_record']

                            sum_price_norm += record['reduction']['sum_price_normalization']
                            sum_hours += record['reduction']['sum_hours_in_record']

                        elif record['group']['year'] == int(benchmark_year):
                            benchmark_record = record['reduction'][y_unit_map] * unit_factor / record['reduction'][
                                'sum_hours_in_record']
                            benchmark_consumption.append([value, benchmark_record])
                            benchmark_diff.append([value, 0])

                            # update totals
                            benchmark_total += record['reduction']['sum_btu'] * mmbtu_unit_factor / record['reduction'][
                                'sum_hours_in_record']
                            benchmark_hours += record['reduction']['sum_hours_in_record']

                    diff.append([value, benchmark_record - report_record])

        if benchmark_hours == 0:
            benchmark_total = 0
        else:
            benchmark_total = benchmark_total * (reported_hours * 1.0 / benchmark_hours)

        difference = benchmark_total - reported_total
        data.difference = difference

        if sum_hours == 0:
            data.cost_reduction = 0
        else:
            data.cost_reduction = (sum_price_norm * 1.0 / sum_hours) * difference

        if difference != 0:
            data.calculated_at = data.cost_reduction * 1.0 / data.difference
        else:
            data.calculated_at = 0.0
        data.reported_consumption = reported_consumption
        data.benchmark_consumption = benchmark_consumption
        data.diff = diff
        data.benchmark_diff = benchmark_diff
        return {'data': data, 'difference': difference, 'utility_total': utility_total, 'reported_total': reported_total,
                'reported_hours': reported_hours, 'benchmark_total': benchmark_total, 'benchmark_hours': benchmark_hours}

def get_factor(y_units, y_unit_map):
    if y_units == "kva" or y_units == "kvar" or y_units == "pf":
        return 1.0
    if y_unit_map == "sum_btu":
        if y_units == "kbtus":
            return 0.001
        if y_units == "mmbtus":
            return 0.000001
        if y_units == "btus":
            return 1.0
        if y_units == "mcf":
            return 1.0 * math.pow(10, -7)
        if y_units == "therms":
            return 1.00023877 * math.pow(10, -5)
        if y_units == "cf":
            return 0.00098522167
        if y_units == "kwh":
            return .00029307107