from collections import defaultdict
from copy import deepcopy
import locale
import math
import json
import itertools
from api.models.ConsumptionTextReport import ConsumptionTextReport
from api.models.TotalEnergyData import TotalEnergyData
from pdb import set_trace as trace


def get_sic_data(report, sic_code, config, g):
    sic_name = g.uow.sic.get_by_code(sic_code)["name"]

    # get the group descendants for the sic code, that will be used to get their accounts
    descendants = g.uow.sic.get_group_descendants(sic_code)
    accounts = []

    # create lists to hold electric and gas values
    report.entity_electric_account_data = []
    report.entity_gas_account_data = []
    report.entity_all_account_data = []

    # initialize all running totals
    report.entity_electric_utility = 0
    report.entity_electric_reported = 0
    report.entity_electric_benchmark = 0
    report.entity_electric_hours = 0
    report.entity_electric_reported_hours = 0
    report.entity_electric_benchmark_hours = 0
    report.entity_electric_price_normalization = 0
    report.entity_electric_cost_reduction = 0
    report.entity_gas_utility = 0
    report.entity_gas_reported = 0
    report.entity_gas_benchmark = 0
    report.entity_gas_hours = 0
    report.entity_gas_reported_hours = 0
    report.entity_gas_benchmark_hours = 0
    report.entity_gas_price_normalization = 0
    report.entity_gas_cost_reduction = 0

    # set the locale
    locale.setlocale(locale.LC_ALL, '')

    # get all accounts for sic code
    for gr in descendants:
        acc_temp = get_accounts_for_group(gr, config.account_type, config.report_year, config.comparison_type,
                                          config.demand_type, g)
        acc_temp += get_accounts_for_group(gr, config.account_type, config.benchmark_year,
                                           config.comparison_type, config.demand_type, g)
        accounts += acc_temp

    if len(accounts) > 0:
        # get distinct list of account id's for the current group
        accounts_grouped = defaultdict(list)
        for a in accounts:
            accounts_grouped[a[0]].append(a)

        for a in accounts_grouped:
            get_account_data(report, accounts_grouped, a, config, g)

        # get difference, cost reduction, and change for the group electric and gas accounts
        report.entity_electric_difference = report.entity_electric_benchmark - report.entity_electric_reported
        report.entity_gas_difference = report.entity_gas_benchmark - report.entity_gas_reported


        if report.entity_electric_benchmark == 0:
            report.entity_electric_change = 0
        else:
            report.entity_electric_change = (report.entity_electric_difference * 1.0 / report.entity_electric_benchmark) * 100.0

        if report.entity_gas_benchmark == 0:
            report.entity_gas_change = 0
        else:
            report.entity_gas_change = (report.entity_gas_difference * 1.0 / report.entity_gas_benchmark) * 100

        # convert from electric and gas units to mmbtus
        report.entity_electric_utility_btu = report.entity_electric_utility / report.electric_unit_factor * report.btu_unit_factor
        report.entity_electric_reported_btu = report.entity_electric_reported / report.electric_unit_factor * report.btu_unit_factor
        report.entity_electric_benchmark_btu = report.entity_electric_benchmark / report.electric_unit_factor * report.btu_unit_factor

        report.entity_gas_utility_btu = report.entity_gas_utility / report.gas_unit_factor * report.btu_unit_factor
        report.entity_gas_reported_btu = report.entity_gas_reported / report.gas_unit_factor * report.btu_unit_factor
        report.entity_gas_benchmark_btu = report.entity_gas_benchmark / report.gas_unit_factor * report.btu_unit_factor

        # find values for all accounts by summing the electric and gas account running totals
        report.entity_all_utility = report.entity_electric_utility_btu + report.entity_gas_utility_btu
        report.entity_all_reported = report.entity_electric_reported_btu + report.entity_gas_reported_btu
        report.entity_all_benchmark = report.entity_electric_benchmark_btu + report.entity_gas_benchmark_btu
        report.entity_all_price_normalization = report.entity_electric_price_normalization + report.entity_gas_price_normalization
        report.entity_all_hours = report.entity_electric_hours + report.entity_gas_hours
        report.entity_all_benchmark_hours = report.entity_electric_benchmark_hours + report.entity_gas_benchmark_hours
        report.entity_all_reported_hours = report.entity_electric_reported_hours + report.entity_gas_reported_hours
        report.entity_all_cost_reduction = report.entity_electric_cost_reduction + report.entity_gas_cost_reduction

        if report.entity_all_benchmark_hours == 0:
            report.entity_all_benchmark = 0
        else:
            report.entity_all_benchmark = report.entity_all_benchmark * (report.entity_all_reported_hours * 1.0 / report.entity_all_benchmark_hours)

        # get difference, cost reduction, and change for all of the accounts
        report.entity_all_difference = report.entity_all_benchmark - report.entity_all_reported

        if report.entity_all_benchmark == 0:
            report.entity_all_change = 0
        else:
            report.entity_all_change = (report.entity_all_difference * 1.0 / report.entity_all_benchmark) * 100

        # insert a new record in the report.entitys_data list, which will be used to create the tables later
        report.entity_data.append(
            {'organization_name': sic_name, 'data': report.entity_all_account_data,
             'accounts_utility_total': "{:,d}".format(int(report.entity_all_utility)),
             'accounts_reported_total': "{:,d}".format(int(report.entity_all_reported)),
             'accounts_benchmark_total': "{:,d}".format(int(report.entity_all_benchmark)),
             'accounts_difference_total': "{:,d}".format(int(report.entity_all_difference)),
             'accounts_change_total': "{:10.2f}%".format(report.entity_all_change),
             'accounts_savings_total': locale.currency(report.entity_all_cost_reduction),
             'electric_accounts': {'data': report.entity_electric_account_data,
                                   'total_electric_utility': "{:,d}".format(int(report.entity_electric_utility)),
                                   'total_electric_reported': "{:,d}".format(int(report.entity_electric_reported)),
                                   'total_electric_benchmark': "{:,d}".format(int(report.entity_electric_benchmark)),
                                   'total_electric_difference': "{:,d}".format(int(report.entity_electric_difference)),
                                   'total_electric_change': "{:10.2f}%".format(report.entity_electric_change),
                                   'total_electric_savings': locale.currency(report.entity_electric_cost_reduction)
             },
             'gas_accounts': {'data': report.entity_gas_account_data,
                              'total_gas_utility': "{:,d}".format(int(report.entity_gas_utility)),
                              'total_gas_reported': "{:,d}".format(int(report.entity_gas_reported)),
                              'total_gas_benchmark': "{:,d}".format(int(report.entity_gas_benchmark)),
                              'total_gas_difference': "{:,d}".format(int(report.entity_gas_difference)),
                              'total_gas_change': "{:10.2f}%".format(report.entity_gas_change),
                              'total_gas_savings': locale.currency(report.entity_gas_cost_reduction)
             }})

        # update the grand_total running totals
        report.grand_total_utility += report.entity_all_utility
        report.grand_total_reported += report.entity_all_reported
        report.grand_total_benchmark += report.entity_all_benchmark
        report.grand_total_hours += report.entity_all_hours
        report.grand_total_reported_hours += report.entity_all_reported_hours
        report.grand_total_benchmark_hours += report.entity_all_benchmark_hours
        report.grand_total_price_normalization += report.entity_all_price_normalization
        report.grand_total_cost_reduction += report.entity_all_cost_reduction


def generate_consumptiontext_report(config, entity_type, g):
    main_table = {'organization_data': [], 'total_data': {}}

    report = ConsumptionTextReport()
    # get the electric and gas unit factors
    report.y_unit_map = 'sum_btu'
    report.electric_unit_factor = get_factor(config.electric_units, report.y_unit_map)
    report.gas_unit_factor = get_factor(config.gas_units, report.y_unit_map)
    report.btu_unit_factor = get_factor(config.btu_units, report.y_unit_map)

    # get the conversion factors from the electric/gas/btu unit factor to mmbtu
    report.electric_to_mmbtu_factor = 1 / report.electric_unit_factor * get_factor('mmbtus', report.y_unit_map)
    report.gas_to_mmbtu_factor = 1 / report.gas_unit_factor * get_factor('mmbtus', report.y_unit_map)
    report.btu_to_mmbtu_factor = 1 / report.btu_unit_factor * get_factor('mmbtus', report.y_unit_map)


    # create list that will hold all table information
    report.entity_data = []

    # initialize running totals for all reporting entities
    report.grand_total_utility = 0
    report.grand_total_benchmark = 0
    report.grand_total_reported = 0
    report.grand_total_hours = 0
    report.grand_total_reported_hours = 0
    report.grand_total_benchmark_hours = 0
    report.grand_total_price_normalization = 0
    report.grand_total_cost_reduction = 0

    # set the locale
    locale.setlocale(locale.LC_ALL, '')

    for entity_id in config.entity_ids:
        if entity_type.lower() == 'groups':
            # get the data for each group, which in turn gets the data for each account
            get_group_data(report, entity_id, config, g)

            entity_name = g.uow.groups.get_group_by_id(entity_id).name
        elif entity_type.lower() == 'sic':
            # get the data for each sic code, which in turn gets the data for each account
            get_sic_data(report, entity_id, config, g)

            entity_name = g.uow.sic.get_by_code(entity_id)['name']
        else:  # naics
            # get the data for each naics code, which in turn gets the data for each account
            get_naics_data(report, entity_id, config, g)

            entity_name = g.uow.naics.get_by_code(entity_id)["name"]

        # add new entry to the main table
        main_table['organization_data'].append(
            {'organization_name': entity_name, 'utility': "{:,d}".format(int(report.entity_all_utility)),
             'reported_utility': "{:,d}".format(int(report.entity_all_reported)),
             'benchmark_utility': "{:,d}".format(int(report.entity_all_benchmark)),
             'difference': "{:,d}".format(int(report.entity_all_difference)),
             'change': "{:10.2f}%".format(report.entity_all_change),
             'savings': locale.currency(report.entity_all_cost_reduction)})

        # reset the entity_all fields
        report.entity_all_utility = 0
        report.entity_all_reported = 0
        report.entity_all_benchmark = 0
        report.entity_all_difference = 0
        report.entity_all_change = 0
        report.entity_all_cost_reduction = 0
        report.entity_all_reported_hours = 0
        report.entity_all_benchmark_hours = 0
        report.entity_all_hours = 0
        report.entity_all_price_normalization = 0

    # get difference, change, and cost_reduction for all reporting entities

    report.grand_total_difference = report.grand_total_benchmark - report.grand_total_reported

    if report.grand_total_benchmark == 0:
        report.grand_total_change = 0.0
    else:
        report.grand_total_change = (report.grand_total_difference * 1.0 / report.grand_total_benchmark) * 100

    main_table['total_data'] = {'utility': "{:,d}".format(int(report.grand_total_utility)),
                                'reported_utility': "{:,d}".format(int(report.grand_total_reported)),
                                'benchmark_utility': "{:,d}".format(int(report.grand_total_benchmark)),
                                'difference': "{:,d}".format(int(report.grand_total_difference)),
                                'change': "{:10.2f}%".format(report.grand_total_change),
                                'savings': locale.currency(report.grand_total_cost_reduction)}

    # get the proper organization column title
    if entity_type.lower() == 'groups':
        column_title = 'Group'
    elif entity_type.lower() == 'sic':
        column_title = 'SIC Code'
    else:  # naics
        column_title = 'NAICS Code'

    return {'main_table': main_table, 'detailed_tables': report.entity_data, 'organization_column_title': column_title,
         'btu_units': get_y_unit_label(config.btu_units), 'electric_units': get_y_unit_label(config.electric_units),
         'gas_units': get_y_unit_label(config.gas_units)}


def get_group_data(report, group_id, config, g):
    group_name = g.uow.groups.get_group_by_id(group_id).name
    descendants = g.uow.groups.get_descendants(group_id)
    accounts = []

    # create lists to hold electric and gas values
    report.entity_electric_account_data = []
    report.entity_gas_account_data = []
    report.entity_all_account_data = []

    # initialize all running totals
    report.entity_electric_utility = 0
    report.entity_electric_reported = 0
    report.entity_electric_benchmark = 0
    report.entity_electric_hours = 0
    report.entity_electric_reported_hours = 0
    report.entity_electric_benchmark_hours = 0
    report.entity_electric_price_normalization = 0
    report.entity_electric_cost_reduction = 0
    report.entity_gas_utility = 0
    report.entity_gas_reported = 0
    report.entity_gas_benchmark = 0
    report.entity_gas_hours = 0
    report.entity_gas_reported_hours = 0
    report.entity_gas_benchmark_hours = 0
    report.entity_gas_price_normalization = 0
    report.entity_gas_cost_reduction = 0

    # set the locale
    locale.setlocale(locale.LC_ALL, '')

    # get all accounts for group and descendants
    for gr in descendants:
        acc_temp = get_accounts_for_group(gr['id'], config.account_type, config.report_year, config.comparison_type,
                                          config.demand_type, g)
        acc_temp += get_accounts_for_group(gr['id'], config.account_type, config.benchmark_year,
                                           config.comparison_type, config.demand_type, g)
        accounts += acc_temp

    if len(accounts) > 0:
        # get distinct list of account id's for the current group
        accounts_grouped = defaultdict(list)
        for a in accounts:
            accounts_grouped[a[0]].append(a)

        for a in accounts_grouped:
            get_account_data(report, accounts_grouped, a, config, g)
        print(report.entity_all_account_data)
        trace()
        # get difference, cost reduction, and change for the group electric and gas accounts
        report.entity_electric_difference = report.entity_electric_benchmark - report.entity_electric_reported
        report.entity_gas_difference = report.entity_gas_benchmark - report.entity_gas_reported


        if report.entity_electric_benchmark == 0:
            report.entity_electric_change = 0
        else:
            report.entity_electric_change = (report.entity_electric_difference * 1.0 / report.entity_electric_benchmark) * 100.0

        if report.entity_gas_benchmark == 0:
            report.entity_gas_change = 0
        else:
            report.entity_gas_change = (report.entity_gas_difference * 1.0 / report.entity_gas_benchmark) * 100

        # convert from electric and gas units to mmbtus
        report.entity_electric_utility_btu = report.entity_electric_utility / report.electric_unit_factor * report.btu_unit_factor
        report.entity_electric_reported_btu = report.entity_electric_reported / report.electric_unit_factor * report.btu_unit_factor
        report.entity_electric_benchmark_btu = report.entity_electric_benchmark / report.electric_unit_factor * report.btu_unit_factor

        report.entity_gas_utility_btu = report.entity_gas_utility / report.gas_unit_factor * report.btu_unit_factor
        report.entity_gas_reported_btu = report.entity_gas_reported / report.gas_unit_factor * report.btu_unit_factor
        report.entity_gas_benchmark_btu = report.entity_gas_benchmark / report.gas_unit_factor * report.btu_unit_factor

        # find values for all accounts by summing the electric and gas account running totals
        report.entity_all_utility = report.entity_electric_utility_btu + report.entity_gas_utility_btu
        report.entity_all_reported = report.entity_electric_reported_btu + report.entity_gas_reported_btu
        report.entity_all_benchmark = report.entity_electric_benchmark_btu + report.entity_gas_benchmark_btu
        report.entity_all_price_normalization = report.entity_electric_price_normalization + report.entity_gas_price_normalization
        report.entity_all_hours = report.entity_electric_hours + report.entity_gas_hours
        report.entity_all_benchmark_hours = report.entity_electric_benchmark_hours + report.entity_gas_benchmark_hours
        report.entity_all_reported_hours = report.entity_electric_reported_hours + report.entity_gas_reported_hours
        report.entity_all_cost_reduction = report.entity_electric_cost_reduction + report.entity_gas_cost_reduction

        if report.entity_all_benchmark_hours == 0:
            report.entity_all_benchmark = 0
        else:
            report.entity_all_benchmark = report.entity_all_benchmark * (report.entity_all_reported_hours * 1.0 / report.entity_all_benchmark_hours)

        # get difference, cost reduction, and change for all of the accounts
        report.entity_all_difference = report.entity_all_benchmark - report.entity_all_reported

        if report.entity_all_benchmark == 0:
            report.entity_all_change = 0
        else:
            report.entity_all_change = (report.entity_all_difference * 1.0 / report.entity_all_benchmark) * 100

        # insert a new record in the report.entitys_data list, which will be used to create the tables later
        report.entity_data.append(
            {'organization_name': group_name, 'data': report.entity_all_account_data,
             'accounts_utility_total': "{:,d}".format(int(report.entity_all_utility)),
             'accounts_reported_total': "{:,d}".format(int(report.entity_all_reported)),
             'accounts_benchmark_total': "{:,d}".format(int(report.entity_all_benchmark)),
             'accounts_difference_total': "{:,d}".format(int(report.entity_all_difference)),
             'accounts_change_total': "{:10.2f}%".format(report.entity_all_change),
             'accounts_savings_total': locale.currency(report.entity_all_cost_reduction),
             'electric_accounts': {'data': report.entity_electric_account_data,
                                   'total_electric_utility': "{:,d}".format(int(report.entity_electric_utility)),
                                   'total_electric_reported': "{:,d}".format(int(report.entity_electric_reported)),
                                   'total_electric_benchmark': "{:,d}".format(int(report.entity_electric_benchmark)),
                                   'total_electric_difference': "{:,d}".format(int(report.entity_electric_difference)),
                                   'total_electric_change': "{:10.2f}%".format(report.entity_electric_change),
                                   'total_electric_savings': locale.currency(report.entity_electric_cost_reduction)
             },
             'gas_accounts': {'data': report.entity_gas_account_data,
                              'total_gas_utility': "{:,d}".format(int(report.entity_gas_utility)),
                              'total_gas_reported': "{:,d}".format(int(report.entity_gas_reported)),
                              'total_gas_benchmark': "{:,d}".format(int(report.entity_gas_benchmark)),
                              'total_gas_difference': "{:,d}".format(int(report.entity_gas_difference)),
                              'total_gas_change': "{:10.2f}%".format(report.entity_gas_change),
                              'total_gas_savings': locale.currency(report.entity_gas_cost_reduction)
             }})

        # update the grand_total running totals
        report.grand_total_utility += report.entity_all_utility
        report.grand_total_reported += report.entity_all_reported
        report.grand_total_benchmark += report.entity_all_benchmark
        report.grand_total_hours += report.entity_all_hours
        report.grand_total_reported_hours += report.entity_all_reported_hours
        report.grand_total_benchmark_hours += report.entity_all_benchmark_hours
        report.grand_total_price_normalization += report.entity_all_price_normalization
        report.grand_total_cost_reduction += report.entity_all_cost_reduction



def get_naics_data(report, naics_code, config, g):
    naics_name = g.uow.naics.get_by_code(naics_code)["name"]

    # get the group descendants for the naics code, that will be used to get their accounts
    descendants = g.uow.naics.get_group_descendants(naics_code)
    accounts = []

    # create lists to hold electric and gas values
    report.entity_electric_account_data = []
    report.entity_gas_account_data = []
    report.entity_all_account_data = []

    # initialize all running totals
    report.entity_electric_utility = 0
    report.entity_electric_reported = 0
    report.entity_electric_benchmark = 0
    report.entity_electric_hours = 0
    report.entity_electric_reported_hours = 0
    report.entity_electric_benchmark_hours = 0
    report.entity_electric_price_normalization = 0
    report.entity_electric_cost_reduction = 0
    report.entity_gas_utility = 0
    report.entity_gas_reported = 0
    report.entity_gas_benchmark = 0
    report.entity_gas_hours = 0
    report.entity_gas_reported_hours = 0
    report.entity_gas_benchmark_hours = 0
    report.entity_gas_price_normalization = 0
    report.entity_gas_cost_reduction = 0

    # set the locale
    locale.setlocale(locale.LC_ALL, '')

    # get all accounts for naics code
    for gr in descendants:
        acc_temp = get_accounts_for_group(gr, config.account_type, config.report_year, config.comparison_type,
                                          config.demand_type, g)
        acc_temp += get_accounts_for_group(gr, config.account_type, config.benchmark_year,
                                           config.comparison_type, config.demand_type, g)
        accounts += acc_temp

    if len(accounts) > 0:
        # get distinct list of account id's for the current group
        accounts_grouped = defaultdict(list)
        for a in accounts:
            accounts_grouped[a[0]].append(a)

        for a in accounts_grouped:
            get_account_data(report, accounts_grouped, a, config, g)

        # get difference, cost reduction, and change for the group electric and gas accounts
        report.entity_electric_difference = report.entity_electric_benchmark - report.entity_electric_reported
        report.entity_gas_difference = report.entity_gas_benchmark - report.entity_gas_reported


        if report.entity_electric_benchmark == 0:
            report.entity_electric_change = 0
        else:
            report.entity_electric_change = (report.entity_electric_difference * 1.0 / report.entity_electric_benchmark) * 100.0

        if report.entity_gas_benchmark == 0:
            report.entity_gas_change = 0
        else:
            report.entity_gas_change = (report.entity_gas_difference * 1.0 / report.entity_gas_benchmark) * 100

        # convert from electric and gas units to mmbtus
        report.entity_electric_utility_btu = report.entity_electric_utility / report.electric_unit_factor * report.btu_unit_factor
        report.entity_electric_reported_btu = report.entity_electric_reported / report.electric_unit_factor * report.btu_unit_factor
        report.entity_electric_benchmark_btu = report.entity_electric_benchmark / report.electric_unit_factor * report.btu_unit_factor

        report.entity_gas_utility_btu = report.entity_gas_utility / report.gas_unit_factor * report.btu_unit_factor
        report.entity_gas_reported_btu = report.entity_gas_reported / report.gas_unit_factor * report.btu_unit_factor
        report.entity_gas_benchmark_btu = report.entity_gas_benchmark / report.gas_unit_factor * report.btu_unit_factor

        # find values for all accounts by summing the electric and gas account running totals
        report.entity_all_utility = report.entity_electric_utility_btu + report.entity_gas_utility_btu
        report.entity_all_reported = report.entity_electric_reported_btu + report.entity_gas_reported_btu
        report.entity_all_benchmark = report.entity_electric_benchmark_btu + report.entity_gas_benchmark_btu
        report.entity_all_price_normalization = report.entity_electric_price_normalization + report.entity_gas_price_normalization
        report.entity_all_hours = report.entity_electric_hours + report.entity_gas_hours
        report.entity_all_benchmark_hours = report.entity_electric_benchmark_hours + report.entity_gas_benchmark_hours
        report.entity_all_reported_hours = report.entity_electric_reported_hours + report.entity_gas_reported_hours
        report.entity_all_cost_reduction = report.entity_electric_cost_reduction + report.entity_gas_cost_reduction

        if report.entity_all_benchmark_hours == 0:
            report.entity_all_benchmark = 0
        else:
            report.entity_all_benchmark = report.entity_all_benchmark * (report.entity_all_reported_hours * 1.0 / report.entity_all_benchmark_hours)

        # get difference, cost reduction, and change for all of the accounts
        report.entity_all_difference = report.entity_all_benchmark - report.entity_all_reported

        if report.entity_all_benchmark == 0:
            report.entity_all_change = 0
        else:
            report.entity_all_change = (report.entity_all_difference * 1.0 / report.entity_all_benchmark) * 100

        # insert a new record in the report.entitys_data list, which will be used to create the tables later
        report.entity_data.append(
            {'organization_name': naics_name, 'data': report.entity_all_account_data,
             'accounts_utility_total': "{:,d}".format(int(report.entity_all_utility)),
             'accounts_reported_total': "{:,d}".format(int(report.entity_all_reported)),
             'accounts_benchmark_total': "{:,d}".format(int(report.entity_all_benchmark)),
             'accounts_difference_total': "{:,d}".format(int(report.entity_all_difference)),
             'accounts_change_total': "{:10.2f}%".format(report.entity_all_change),
             'accounts_savings_total': locale.currency(report.entity_all_cost_reduction),
             'electric_accounts': {'data': report.entity_electric_account_data,
                                   'total_electric_utility': "{:,d}".format(int(report.entity_electric_utility)),
                                   'total_electric_reported': "{:,d}".format(int(report.entity_electric_reported)),
                                   'total_electric_benchmark': "{:,d}".format(int(report.entity_electric_benchmark)),
                                   'total_electric_difference': "{:,d}".format(int(report.entity_electric_difference)),
                                   'total_electric_change': "{:10.2f}%".format(report.entity_electric_change),
                                   'total_electric_savings': locale.currency(report.entity_electric_cost_reduction)
             },
             'gas_accounts': {'data': report.entity_gas_account_data,
                              'total_gas_utility': "{:,d}".format(int(report.entity_gas_utility)),
                              'total_gas_reported': "{:,d}".format(int(report.entity_gas_reported)),
                              'total_gas_benchmark': "{:,d}".format(int(report.entity_gas_benchmark)),
                              'total_gas_difference': "{:,d}".format(int(report.entity_gas_difference)),
                              'total_gas_change': "{:10.2f}%".format(report.entity_gas_change),
                              'total_gas_savings': locale.currency(report.entity_gas_cost_reduction)
             }})

        # update the grand_total running totals
        report.grand_total_utility += report.entity_all_utility
        report.grand_total_reported += report.entity_all_reported
        report.grand_total_benchmark += report.entity_all_benchmark
        report.grand_total_hours += report.entity_all_hours
        report.grand_total_reported_hours += report.entity_all_reported_hours
        report.grand_total_benchmark_hours += report.entity_all_benchmark_hours
        report.grand_total_price_normalization += report.entity_all_price_normalization
        report.grand_total_cost_reduction += report.entity_all_cost_reduction


def get_account_data(report, accounts_grouped, acc, config, g):
    """
    Gets the account energy record information
    :param report: the ConsumptionTextReport object that the data is being stored in
    :param accounts_grouped: distinct list of accounts for a given group
    :param account: the current account
    :param config: report configuration
    :param g:
    :return:
    """
    # initialize all values used per account
    report.account_utility = 0
    report.account_reported = 0
    report.account_benchmark = 0
    report.account_hours = 0
    report.account_reported_hours = 0
    report.account_price_normalization = 0
    report.account_benchmark_hours = 0
    report.account_cost_reduction = 0

    reported_cost = 0
    benchmark_cost = 0

    # set the locale
    locale.setlocale(locale.LC_ALL, '')

    # get the query entries for the account
    account = accounts_grouped[acc]
    report_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(account, group_by_account=True)

    # get the type of group to figure out the proper cost factor to use
    account_model = g.uow.accounts.get_by_id(acc)
    if account_model.type.lower() == 'electric':
        cost_unit_factor = get_factor('kwh', 'sum_btu')
    else:
        cost_unit_factor = get_factor('mcf', 'sum_btu')

    grouped = defaultdict(list)

    # group by each value returned from the query
    for d in report_data:
        grouped[d['group']['value']].append(d)

    # loop through all records returned from the query
    for value in grouped:
        entry = grouped[value]

        # handle same year in a simple way
        if config.report_year == config.benchmark_year:
            report_record_hours = entry[0]['reduction']['sum_hours_in_record']
            report_record_value = entry[0]['reduction'][report.y_unit_map] / report_record_hours

            # update report, utiltiy, and benchmark values
            report.account_utility += report_record_value

            report.account_reported += report_record_value
            report.account_reported_hours += report_record_hours

            report.account_benchmark += report_record_value
            report.account_benchmark_hours += benchmark_record_hours

        # search the entry for the report year and add data to the account utility
        for rec in entry:
            if rec['group']['year'] == config.report_year:
                report.account_utility += rec['reduction'][report.y_unit_map] / rec['reduction']['sum_hours_in_record']

        # if the data exists for both years
        if len(entry) > 1:
            benchmark_record = 0
            reported_avg_size = 0
            benchmark_avg_size = 0
            benchmark_record_hours = 0
            benchmark_record_btu_normalized = 0
            report_price_per_unit = 0
            for record in entry:
                if record['group']['year'] == config.report_year:
                    report_record_hours = record['reduction']['sum_hours_in_record']

                    report_record_value = record['reduction'][report.y_unit_map] * 1.0 / report_record_hours
                    reported_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / report_record_hours
                    report_price_per_unit = record['reduction']['sum_price_normalization'] * 1.0 / report_record_hours

                    reported_cost += (report_record_value * cost_unit_factor * report_price_per_unit)

                    # update the totals for the report year
                    report.account_reported += record['reduction'][report.y_unit_map] * 1.0 / report_record_hours
                    report.account_reported_hours += report_record_hours

                    # update the overall totals
                    report.account_price_normalization += record['reduction']['sum_price_normalization']
                elif record['group']['year'] == config.benchmark_year:
                    benchmark_record_hours = record['reduction']['sum_hours_in_record']

                    benchmark_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / benchmark_record_hours
                    benchmark_record_btu_normalized = record['reduction'][report.y_unit_map]

            # normalize the benchmark value
            size_ratio = reported_avg_size * 1.0 / benchmark_avg_size
            benchmark_record_btu_normalized *= size_ratio
            benchmark_record_btu_normalized /= benchmark_record_hours
            benchmark_cost += (benchmark_record_btu_normalized * cost_unit_factor * report_price_per_unit)

            # update the totals for the benchmark year
            report.account_benchmark += benchmark_record_btu_normalized
            report.account_benchmark_hours += benchmark_record_hours
    # get the data using the electic/gas unit factors
    calculate_electric_and_gas_data_for_account(report, account_model, reported_cost, benchmark_cost)

    # create a dictionary using the account's data to be used later on
    account_data = {'account_name': account_model.name, 'utility': "{:,d}".format(int(report.account_utility)),
         'reported_utility': "{:,d}".format(int(report.account_reported)),
         'benchmark_utility': "{:,d}".format(int(report.account_benchmark)),
         'difference': "{:,d}".format(int(report.account_difference)),
         'change': "{:10.2f}%".format(report.account_change),
         'savings': locale.currency(report.account_cost_reduction)}

    # get the data using the btu units
    #get_btu_data_for_account(report, account_model, reported_cost, benchmark_cost)

    # create dictionary object to be used in the table
    btu_account_data = {'account_name': account_model.name,
                          'utility': "{:,d}".format(int(report.account_utility_btu)),
                          'reported_utility': "{:,d}".format(int(report.account_reported_btu)),
                          'benchmark_utility': "{:,d}".format(int(report.account_benchmark_btu)),
                          'difference': "{:,d}".format(int(report.account_difference_btu)),
                          'change': "{:10.2f}%".format(report.account_change_btu),
                          'savings': locale.currency(report.account_cost_reduction)}

    report.entity_all_account_data.append(btu_account_data)

    # add to totals
    if account_model.type.lower() == 'electric':
        # increase the group's electric account totals
        report.entity_electric_utility += report.account_utility
        report.entity_electric_reported += report.account_reported
        report.entity_electric_benchmark += report.account_benchmark
        report.entity_electric_price_normalization += report.account_price_normalization
        report.entity_electric_reported_hours += report.account_reported_hours
        report.entity_electric_benchmark_hours += report.account_benchmark_hours
        report.entity_electric_hours += report.account_hours
        report.entity_electric_cost_reduction += report.account_cost_reduction

        # add account data to the list of electric accounts for use in table
        report.entity_electric_account_data.append(account_data)
    else:
        # increase the group's gas account totals
        report.entity_gas_utility += report.account_utility
        report.entity_gas_benchmark += report.account_benchmark
        report.entity_gas_reported += report.account_reported
        report.entity_gas_price_normalization += report.account_price_normalization
        report.entity_gas_hours += report.account_hours
        report.entity_gas_reported_hours += report.account_reported_hours
        report.entity_gas_benchmark_hours += report.account_benchmark_hours
        report.entity_gas_cost_reduction += report.account_cost_reduction

        # add account data to the list of gas accounts for use in table
        report.entity_gas_account_data.append(account_data)


def calculate_electric_and_gas_data_for_account(report, account_model, reported_cost, benchmark_cost):
    # update the records found using the unit factors for the different account types
    if account_model.type.lower() == 'electric':
        report.account_utility *= report.electric_unit_factor
        report.account_reported *= report.electric_unit_factor
        report.account_benchmark *= report.electric_unit_factor
    else:
        report.account_utility *= report.gas_unit_factor
        report.account_reported *= report.gas_unit_factor
        report.account_benchmark *= report.gas_unit_factor

    # update the total hours
    report.account_hours += (report.account_benchmark_hours + report.account_reported_hours)

    report.account_difference = report.account_benchmark - report.account_reported

    # get cost reduction
    report.account_cost_reduction = benchmark_cost - reported_cost

    if report.account_benchmark == 0:
        report.account_change = 0
    else:
        report.account_change = (report.account_difference * 1.0 / report.account_benchmark) * 100


def get_btu_data_for_account(report, account_model, reported_cost, benchmark_cost):
    # convert to mmbtu's for the group table that contains all accounts
    if account_model.type.lower() == 'electric':
        report.account_utility_btu = report.account_utility / report.electric_unit_factor * report.btu_unit_factor
        report.account_reported_btu = report.account_reported / report.electric_unit_factor * report.btu_unit_factor
        report.account_benchmark_btu = report.account_benchmark / report.electric_unit_factor * report.btu_unit_factor
    else:
        report.account_utility_btu = report.account_utility / report.gas_unit_factor * report.btu_unit_factor
        report.account_reported_btu = report.account_reported / report.gas_unit_factor * report.btu_unit_factor
        report.account_benchmark_btu = report.account_benchmark / report.gas_unit_factor * report.btu_unit_factor

    report.account_difference_btu = report.account_benchmark_btu - report.account_reported_btu

    if report.account_benchmark_btu == 0:
        report.account_change_btu = 0
    else:
        report.account_change_btu = (report.account_difference_btu * 1.0 / report.account_benchmark_btu) * 100


def get_accounts_for_group(group_id, account_type, report_year, comparison_type, demand_type, g):
    accounts = []
    # if demand type is specified, it needs to be included
    if demand_type != 'all':
        # find accounts for all or only electric/gas
        if account_type != 'all':
            acc = g.uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
            for a in acc:
                accounts.append([a['id'], comparison_type, int(report_year), demand_type])
        else:
            for account in g.uow.accounts.get_all_for_group(group_id):
                accounts.append([account['id'], comparison_type, report_year, demand_type])
    else:
        # no demand type, so only worry if account type is all or only electric/gas
        if account_type != 'all':
            acc = g.uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
            for a in acc:
                accounts.append([a['id'], comparison_type, report_year])
        else:
            for account in g.uow.accounts.get_all_for_group(group_id):
                accounts.append([account['id'], comparison_type, report_year])
    return accounts


def get_factor(y_units, y_unit_map):
    if y_units == "kva" or y_units == "kvar" or y_units == "pf" or y_unit_map == "sum_kvar" or y_unit_map == "kva" or y_unit_map == "pf":
        return 1.0
    if y_unit_map == "sum_btu":
        if y_units == "kbtus":
            return 0.001
        if y_units == "mmbtus":
            return 0.000001
        if y_units == "btus":
            return 1.0
        if y_units == "mcf":
            return 9.75e-7
        if y_units == "therms":
            return 1.00023877 * math.pow(10, -5)
        if y_units == "cf":
            return 9.75e-7 * 1000000.
        if y_units == "kwh":
            return .00029307107
        if y_units == "mwh":
            return .00029307107 * (1 / 1000.0)
        if y_units == "gwh":
            return .00029307107 * math.pow(10, -6)
        if y_units == "twh":
            return .00029307107 * math.pow(10, -9)


def get_y_unit_label(y_units):
    if y_units == "kva":
        return "Kva"
    elif y_units == "kw":
        return "kW"
    elif y_units == "kvar":
        return "Kvar"
    elif y_units == "pf":
        return "Pf"
    elif y_units == "kbtus" or y_units == "kbtu":
        return "kBtus"
    elif y_units == "mmbtus" or y_units == "mmbtu":
        return "MMBtus"
    elif y_units == "btus" or y_units == "btu":
        return "Btus"
    elif y_units == "mcf":
        return "Mcf"
    elif y_units == "therms":
        return  "Therms"
    elif y_units == "cf":
        return "cf"
    elif y_units == "kwh":
        return "kWh"
    elif y_units == "mwh":
        return "MWh"
    elif y_units == "gwh":
        return "GWh"
    elif y_units == "twh":
        return "TWh"
    return ""


def get_submitted_contacts(submitted_by_user, submitted_to, g):
    primary_group = g.uow.groups.get_group_by_id(submitted_by_user['primary_group_id'])

    # make sure all data is present
    if 'first_name' in submitted_by_user and 'last_name' in submitted_by_user and 'job_title' in submitted_by_user and \
                    'address' in submitted_by_user and 'city' in submitted_by_user and 'state' in submitted_by_user and \
                    'zip' in submitted_by_user:
        submitted_by_user = primary_group.name + '\n' + submitted_by_user['first_name'] + ' ' + \
                                                 submitted_by_user['last_name'] + ', ' + submitted_by_user['job_title'] + \
                                                 '\n' + submitted_by_user['address'] + '\n' + submitted_by_user['city'] + \
                                                 ', ' + submitted_by_user['state'] + ' ' + submitted_by_user['zip']
    else:
        submitted_by_user = ''

    submitted_group = g.uow.groups.get_group_by_id(submitted_to)
    # make sure all data is present
    if submitted_group and submitted_group.first_name and submitted_group.last_name and submitted_group.job_title and \
            submitted_group.address and submitted_group.city and submitted_group.state and submitted_group.zip:
        submitted_to = submitted_group.name + '\n' + \
                       submitted_group.first_name + ' ' + submitted_group.last_name + ', ' + submitted_group.job_title + \
                       '\n' + submitted_group.address + \
                       '\n' + submitted_group.city + ', ' + submitted_group.state + ' ' + submitted_group.zip
    else:
        submitted_to = ''

    return submitted_by_user, submitted_to


def get_benchmark_year_data(account, data_field_name, consider_demand_type, g):
    """
    Gets the energy data for the benchmark year
    :param account: benchmark account in the form [account_id, comparison_type, year, demand_type (optional)]
    :param data_field_name: units to use
    :param consider_demand_type: specifies weather or not to use a report index where the demand type is checked
    :param g:
    :return: the energy data for the benchmark year grouped by value
    """
    benchmark_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report([account], data_field_name=data_field_name, consider_demand_type=consider_demand_type)

    # turn the raw data into a dictionary, keyed by the x-axis value, with a list of all data associated with that value
    grouped_data = defaultdict(list)
    for d in benchmark_data:
        grouped_data[d['group']['value']].append(d)
    return grouped_data


def calculate_energy_data(account_group, report_year, benchmark_year, same_year, y_units, y_unit_map, unit_factor, account_type):
    """
    Calculates the energy data for the account
    :param y_units: desired units for values
    :param account_type: the type of account for the current account_group (should be 'electric' or 'gas')
    :param account_group: data for the account grouped by value
    :param report_year: current year for the report data
    :param benchmark_year: benchmark year to compare it to
    :param same_year: boolean value stating whether report_year == benchmark_year
    :param y_unit_map: column in the database used to get desired units
    :param unit_factor: factor to multiply the value in the y_unit_map to reach the desired units
    :return: energy data with totals in the form {TotalEnergyData object, utility_total, reported_total, benchmark_total}
    """
    # initialize all variables for this account/year combination
    reported_consumption = []
    diff = []
    benchmark_diff = []
    benchmark_consumption = []

    grouped_keys = list(account_group.keys())
    grouped_keys.sort()

    reported_total = 0
    benchmark_total = 0
    utility_total = 0

    reported_cost = 0
    benchmark_cost = 0

    total_sum_price_norm = 0
    total_sum_hours = 0

    # get the proper factor for calculating cost
    if y_units == 'kva' or y_units == 'kvar':
        cost_unit_factor = get_factor('kwh', 'sum_btu')
    elif account_type.lower() == 'electric':
        # unit factor to change cost from $/kwh to $/btu
        cost_unit_factor = get_factor('kwh', 'sum_btu')
    elif account_type.lower() == 'gas':
        # unit factor to change cost from $/mCf to $/btu
        cost_unit_factor = get_factor('mcf', 'sum_btu')
    else:
        cost_unit_factor = unit_factor


    # if the benchmark year and the current year are the same they will be handled differently
    if same_year:
        for value in grouped_keys:
            entry = account_group[value]
            record_hours = entry[0]['reduction']['sum_hours_in_record']
            record_value = entry[0]['reduction'][y_unit_map] * unit_factor
            record_price_norm = entry[0]['reduction']['sum_price_normalization']

            reported_consumption.append(
                [value, round(record_value / record_hours,5)]
            )

            diff.append([value, 0])
            benchmark_consumption.append(
                [value, round(record_value / record_hours,5)])
            benchmark_diff.append([value, 0])

            # get totals specifying to convert to desired units
            reported_total += record_value
            benchmark_total += record_value
            utility_total += record_value

            # normalize price
            cost_per_unit = record_price_norm * 1.0 / record_hours * unit_factor
            reported_cost += (cost_per_unit * record_value)
            benchmark_cost += (cost_per_unit * record_value)

            total_sum_price_norm += record_price_norm
            total_sum_hours += record_hours
    else:
        # loop through each entry in the keys
        for value in grouped_keys:
            entry = account_group[value]

            # search the entry for the report year and add data to the utility total
            for rec in entry:
                if rec['group']['year'] == report_year:
                    utility_total += rec['reduction'][y_unit_map] * unit_factor

            # if the data exists for both years
            if len(entry) > 1:
                report_record = 0
                benchmark_record = 0
                reported_avg_size = 0
                benchmark_avg_size = 0
                benchmark_record_hours = 0
                benchmark_record_btu_normalized = 0
                report_price_per_unit = 0
                for record in entry:
                    if record['group']['year'] == report_year:
                        report_record_hours = record['reduction']['sum_hours_in_record']
                        report_record_price_norm = record['reduction']['sum_price_normalization']

                        report_record = record['reduction'][y_unit_map] * unit_factor
                        reported_consumption.append([value, round(report_record / report_record_hours, 5)])

                        reported_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / report_record_hours
                        report_price_per_unit = report_record_price_norm * 1.0 / report_record_hours

                        # update totals
                        reported_cost += (record['reduction']['sum_btu'] * cost_unit_factor * report_price_per_unit)
                        reported_total += report_record

                        total_sum_hours += report_record_hours
                        total_sum_price_norm += report_record_price_norm

                    elif record['group']['year'] == benchmark_year:
                        benchmark_record_hours = record['reduction']['sum_hours_in_record']

                        benchmark_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / benchmark_record_hours
                        benchmark_record_btu_normalized = record['reduction']['sum_btu']
                        benchmark_record = record['reduction'][y_unit_map] * unit_factor

                # get the adjusted benchmark value to be more accurate about consumption and prices
                size_ratio = reported_avg_size * 1.0 / benchmark_avg_size
                benchmark_record *= size_ratio

                # size normalize the btu value for proper cost reduction
                benchmark_record_btu_normalized *= size_ratio
                benchmark_cost += (benchmark_record_btu_normalized * cost_unit_factor * report_price_per_unit)
                benchmark_consumption.append([value, round(benchmark_record / benchmark_record_hours, 5)])
                benchmark_diff.append([value, 0])

                diff.append([value, round(benchmark_record - report_record, 5)])

                # update benchmark total
                benchmark_total += benchmark_record

    # create a new data object to be returned
    data = TotalEnergyData()
    data.difference = benchmark_total - reported_total

    data.cost_reduction = -(benchmark_cost - reported_cost)

    if total_sum_hours != 0:
        data.calculated_at = total_sum_price_norm * 1.0 / total_sum_hours
    else:
        data.calculated_at = 0

    data.reported_consumption = reported_consumption
    data.benchmark_consumption = benchmark_consumption
    data.diff = diff
    data.benchmark_diff = benchmark_diff

    return {'data': data,
            'utility_total': utility_total,
            'reported_total': reported_total,
            'benchmark_total': benchmark_total}


def get_total_energy_chart_data_pdf(accounts, report_year, benchmark_year, demand_type, y_units, y_unit_map, g):
    """
    Gets and calculates all data needed for the consumption charts
    :param accounts: list of accounts for which to find data
    :param report_year: report year
    :param benchmark_year: benchmark year
    :param demand_type: 'all'/'peak'/'offpeak'
    :param y_units: the units selected by the user (btu, mmbtu, kwh, etc)
    :param y_unit_map: the mapping of the unit to the database column
    :param g:
    :return: data in the form {'chart_data', 'year_data'}
    """

    data_list = []
    year_grouping = {}
    for account in accounts:
        # get the benchmark data for the account, as all other years will be compared against it
        if demand_type != 'all':
            benchmark_account = [account[0], account[1], benchmark_year, demand_type]
            consider_demand_type = True
        else:
            consider_demand_type = False
            benchmark_account = [account[0], account[1], benchmark_year]

        grouped_data = get_benchmark_year_data(benchmark_account, y_unit_map, consider_demand_type, g)

        # start at the report range low and go through each year
        years_to_go_back = 5
        while years_to_go_back != -1:
            year = report_year - years_to_go_back
            same_year = year == benchmark_year
            unit_factor = get_factor(y_units, y_unit_map)

            # since account is in the form of a list [id, comparison_value, year] we need to set the year
            if consider_demand_type:
                new_account = [account[0], account[1], year, demand_type]
            else:
                new_account = [account[0], account[1], year]

            # send the new account form and the grouped benchmark data (to avoid looping through the benchmark data again)
            report_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report([new_account], data_field_name=y_unit_map,
                                                                                             consider_demand_type=consider_demand_type)

            # create a copy of grouped_data
            account_group = deepcopy(grouped_data)
            for d in report_data:
                account_group[d['group']['value']].append(d)

            account_type = g.uow.accounts.get_by_id(new_account[0]).type
            calculated_totals = calculate_energy_data(account_group, year, benchmark_year, same_year, y_units, y_unit_map, unit_factor, account_type)

            # get the information from the dictionary returned from calculate energy data
            data = calculated_totals['data']
            utility_total = calculated_totals['utility_total']
            reported_total = calculated_totals['reported_total']
            benchmark_total = calculated_totals['benchmark_total']

            # update information for table
            if not year in year_grouping:
                year_grouping[year] = {'utility': utility_total, 'reported': reported_total, 'benchmark': benchmark_total, 'cost_reduction': data.cost_reduction}
            else:
                year_grouping[year] = {'utility': utility_total + year_grouping[year]['utility'],
                                       'reported': reported_total + year_grouping[year]['reported'],
                                       'benchmark': benchmark_total + year_grouping[year]['benchmark'],
                                       'cost_reduction': data.cost_reduction + year_grouping[year]['cost_reduction']}

            # get meta information for account
            data.account_name = g.uow.accounts.get_by_id(account[0]).name
            data.year = year
            data_list.append(data)

            for yr in year_grouping:
                new_dict = {'difference': year_grouping[yr]['benchmark'] - year_grouping[yr]['reported']}
                if year_grouping[yr]['benchmark'] != 0 :
                    new_dict['change'] = ((year_grouping[yr]['benchmark'] - year_grouping[yr]['reported']) * 1.0) / year_grouping[yr]['benchmark'] * 100
                else:
                    new_dict['change'] = 0
                # merge the two dictionaries
                year_grouping[yr] = dict(year_grouping[yr].items() + new_dict.items())

            years_to_go_back -= 1

    return {'chart_data': data_list, 'year_data': year_grouping}


def calculate_pf_data(account_group, report_year, benchmark_year, same_year):
    """
    Calculates the energy data for the account
    :param account_group: data for the account grouped by value
    :param report_year: current year for the report data
    :param benchmark_year: benchmark year to compare it to
    :param same_year: boolean value stating whether report_year == benchmark_year
    :return: TotalEnergyData
    """
    # initialize all variables for this account/year combination
    reported_consumption = []
    diff = []
    benchmark_diff = []
    benchmark_consumption = []

    grouped_keys = list(account_group.keys())
    grouped_keys.sort()

    kwh_unit_factor = get_factor('kwh', 'sum_btu')

    # if the benchmark year and the current year are the same they will be handled differently
    if same_year:
        for value in grouped_keys:
            entry = account_group[value][0]

            record_kwh = entry["reduction"]["sum_btu"] * kwh_unit_factor
            record_kvar = math.sqrt(math.pow(record_kwh,  2) + math.pow(entry["reduction"]["sum_kvar"], 2))
            record_pf = record_kwh * 1.0 / record_kvar

            reported_consumption.append(
                [value, round(record_pf, 5)]
            )

            diff.append([value, 0])
            benchmark_consumption.append(
                [value, round(record_pf, 5)])
            benchmark_diff.append([value, 0])
    else:
        # loop through each entry in the keys
        for value in grouped_keys:
            entry = account_group[value]

            # if the data exists for both years
            if len(entry) > 1:
                record_pf = 0
                reported_avg_size = 0
                benchmark_avg_size = 0
                benchmark_record_btu_normalized = 0
                benchmark_record_kvar_normalized = 0
                for record in entry:
                    if record['group']['year'] == report_year:
                        record_kwh = record["reduction"]["sum_btu"] * kwh_unit_factor
                        record_kvar = math.sqrt(math.pow(record_kwh,  2) + math.pow(record["reduction"]["sum_kvar"], 2))
                        record_pf = record_kwh * 1.0 / record_kvar

                        report_record_hours = record['reduction']['sum_hours_in_record']
                        reported_consumption.append([value, round(record_pf, 5)])

                        reported_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / report_record_hours

                    elif record['group']['year'] == benchmark_year:
                        benchmark_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / record['reduction']['sum_hours_in_record']
                        benchmark_record_btu_normalized = record['reduction']['sum_btu']
                        benchmark_record_kvar_normalized = record["reduction"]["sum_kvar"]

                # normalize the btu and kvar to properly calculate pf
                size_ratio = reported_avg_size * 1.0 / benchmark_avg_size
                benchmark_record_btu_normalized *= size_ratio
                benchmark_record_kvar_normalized *= size_ratio
                benchmark_kwh = benchmark_record_btu_normalized * kwh_unit_factor
                benchmark_kvar = math.sqrt(math.pow(benchmark_kwh, 2) + math.pow(benchmark_record_kvar_normalized, 2))

                benchmark_pf = benchmark_kwh * 1.0 / benchmark_kvar
                benchmark_consumption.append([value, round(benchmark_pf, 5)])
                benchmark_diff.append([value, 0])

                diff.append([value, round(benchmark_pf - record_pf, 5)])

    # create a new data object to be returned
    data = TotalEnergyData()

    data.reported_consumption = reported_consumption
    data.benchmark_consumption = benchmark_consumption
    data.diff = diff
    data.benchmark_diff = benchmark_diff

    return data


def get_pf_chart_data_pdf(accounts, report_year, benchmark_year, demand_type, g):
    """
    Gets and calculates all data needed for power factor charts
    :param accounts: list of accounts for which to find data
    :param report_year: report year
    :param benchmark_year: benchmark year
    :param demand_type: 'all'/'peak'/'offpeak'
    :param g:
    :return: data
    """

    data_list = []

    for account in accounts:
        # get the benchmark data for the account, as all other years will be compared against it
        if demand_type != 'all':
            benchmark_account = [account[0], account[1], benchmark_year, demand_type]
            consider_demand_type = True
        else:
            benchmark_account = [account[0], account[1], benchmark_year]
            consider_demand_type = False

        grouped_data = get_benchmark_year_data(benchmark_account, 'sum_kvar', consider_demand_type, g)

        # go back through five years for each account
        years_to_go_back = 5
        while years_to_go_back != -1:
            year = report_year - years_to_go_back

            same_year = year == benchmark_year

            # since the account is in the form of a list [id, comparison_type, year] we need to set the new year
            if consider_demand_type:
                new_account = [account[0], account[1], year, demand_type]
            else:
                new_account = [account[0], account[1], year]

            # send the new account form and the grouped benchmark data (to avoid looping through the benchmark data again)
            report_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report([new_account], data_field_name='sum_kvar',
                                                                                             consider_demand_type=consider_demand_type)

            # create a copy of grouped_data (benchmark records)
            account_group = deepcopy(grouped_data)
            for d in report_data:
                account_group[d['group']['value']].append(d)

            calculated_totals = calculate_pf_data(account_group, year, benchmark_year, same_year)

            # get the information from the dictionary returned from calculate energy data
            data = calculated_totals

            years_to_go_back -= 1

            # get meta information for account
            data.account_name = g.uow.accounts.get_by_id(account[0]).name
            data.year = year
            data_list.append(data)

    return {'chart_data': data_list}


def int_round(value):
    return int(round(value))


def get_variance_report_data(accounts, account_type, report_year, benchmark_year, demand_type, y_units, y_unit_map, g):
    if demand_type != 'all':
        consider_demand_type = True
    else:
        consider_demand_type = False

    # get unit factor for the selected reporting units
    unit_factor = get_factor(y_units, y_unit_map)

    if len(accounts) > 1:
        # get the variance data
        variance_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(accounts, consider_demand_type=consider_demand_type,
                                                                                             group_by_month=True, group_by_account=True)
    else:
        variance_data = []

    report_year_records = [x for x in variance_data if x["group"]["year"] == report_year]

    # records grouped only by value (each element contains records across the whole year)
    report_year_records_dict_by_value = dict((x["group"]["value"], x) for x in report_year_records)

    # records grouped by month and then value
    report_year_records_dict_by_month_value = dict(
        (month, dict((x["group"]["value"], x) for x in month_records))
        for month, month_records in itertools.groupby(report_year_records, lambda x: x["group"]["month"])
    )

    benchmark_year_records = [x for x in variance_data if x["group"]["year"] == benchmark_year]

    # records grouped only by value (each element contains records across the whole benchmark year)
    benchmark_year_records_dict_by_value = dict((x["group"]["value"], x) for x in benchmark_year_records)

    # records grouped by month and then value
    benchmark_year_records_dict_by_month_value = dict(
        (month, dict((x["group"]["value"], x) for x in month_records))
        for month, month_records in itertools.groupby(benchmark_year_records, lambda x: x["group"]["month"])
    )

    # initialize values so we don't need to continuously check if the key exists while inserting
    initial_values = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
    utility = initial_values.copy()
    actual = initial_values.copy()
    benchmark = initial_values.copy()
    plan = initial_values.copy()
    actual_hours = initial_values.copy()
    benchmark_hours = initial_values.copy()
    cost_variance = initial_values.copy()
    percent_variance = initial_values.copy()

    report_cost = initial_values.copy()
    benchmark_cost = initial_values.copy()

    # get the proper cost factor
    if account_type.lower() == 'electric':
        cost_factor = get_factor('kwh', 'sum_btu')
    else:
        cost_factor = get_factor('mcf', 'sum_btu')

    count = 0

    for month, comparison_values in report_year_records_dict_by_month_value.items():
        for comparison_value, record in report_year_records_dict_by_month_value[month].items():
            report_record_hours = record["reduction"]["sum_hours_in_record"]
            report_record = record["reduction"]["sum_btu"] * 1.0 # / report_record_hours
            report_avg_size = record["reduction"]["sum_size_normalization"] * 1.0 / report_record_hours
            report_price_per_unit = record["reduction"]["sum_price_normalization"] * 1.0 / report_record_hours

            # add to utility before normalization
            utility[month] += report_record

            # try to get data for the benchmark year/month/value match
            try:
                benchmark_data = benchmark_year_records_dict_by_month_value[month][comparison_value]

                benchmark_record_hours = benchmark_data["reduction"]["sum_hours_in_record"]
                benchmark_avg_size = benchmark_data["reduction"]["sum_size_normalization"] * 1.0 / benchmark_record_hours
                size_ratio = report_avg_size / benchmark_avg_size
                benchmark_record = benchmark_data["reduction"]["sum_btu"] * size_ratio * 1.0

                # add to actual and benchmark values
                actual[month] += report_record
                benchmark[month] += benchmark_record

                actual_hours[month] += report_record_hours
                benchmark_hours[month] += benchmark_record_hours

                report_cost[month] += (report_record * cost_factor * report_price_per_unit)
                benchmark_cost[month] += (benchmark_record * cost_factor * report_price_per_unit)
            except KeyError:
                # no data was found, so there is no match and we move to the next value
                continue

    # adjust values for utility to be in desired units
    for key in utility.keys():
        utility[key] *= unit_factor

    # adjust the values to be desired units
    for key in benchmark.keys():
        actual[key] *= unit_factor
        plan[key] = benchmark[key] * 0.97 * unit_factor
        benchmark[key] *= unit_factor
        cost_variance[key] = benchmark_cost[key] - report_cost[key]

    # use monthly_difference for each month to calculate variance properly
    monthly_difference = initial_values.copy()
    for key in monthly_difference.keys():
        monthly_difference[key] = actual[key] - benchmark[key]

        # get the variance
        if benchmark[key] == 0:
            percent_variance[key] = 0
        else:
            percent_variance[key] = (monthly_difference[key] * 1.0 / benchmark[key]) * 100


    utility_list = utility.values()
    actual_list = actual.values()
    benchmark_list = benchmark.values()
    plan_list = plan.values()
    cost_variance_list = cost_variance.values()
    percent_variance_list = percent_variance.values()

    # get the quarter and annual data for each data type
    utility_list.insert(3, utility_list[0] + utility_list[1] + utility_list[2])
    utility_list.insert(7, utility_list[4] + utility_list[5] + utility_list[6])
    utility_list.insert(11, utility_list[8] + utility_list[9] + utility_list[10])
    utility_list.insert(15, utility_list[12] + utility_list[13] + utility_list[14])
    utility_list.append(utility_list[3] + utility_list[7] + utility_list[11] + utility_list[15])

    actual_list.insert(3, actual_list[0] + actual_list[1] + actual_list[2])
    actual_list.insert(7, actual_list[4] + actual_list[5] + actual_list[6])
    actual_list.insert(11, actual_list[8] + actual_list[9] + actual_list[10])
    actual_list.insert(15, actual_list[12] + actual_list[13] + actual_list[14])
    actual_list.append(actual_list[3] + actual_list[7] + actual_list[11] + actual_list[15])

    benchmark_list.insert(3, benchmark_list[0] + benchmark_list[1] + benchmark_list[2])
    benchmark_list.insert(7, benchmark_list[4] + benchmark_list[5] + benchmark_list[6])
    benchmark_list.insert(11, benchmark_list[8] + benchmark_list[9] + benchmark_list[10])
    benchmark_list.insert(15, benchmark_list[12] + benchmark_list[13] + benchmark_list[14])
    benchmark_list.append(benchmark_list[3] + benchmark_list[7] + benchmark_list[11] + benchmark_list[15])

    plan_list.insert(3, benchmark_list[3] * 0.97)
    plan_list.insert(7, benchmark_list[7] * 0.97)
    plan_list.insert(11, benchmark_list[11] * 0.97)
    plan_list.insert(15, benchmark_list[15] * 0.97)
    plan_list.append(benchmark_list[16] * 0.97)

    cost_variance_list.insert(3, cost_variance_list[0] + cost_variance_list[1] + cost_variance_list[2])
    cost_variance_list.insert(7, cost_variance_list[4] + cost_variance_list[5] + cost_variance_list[6])
    cost_variance_list.insert(11, cost_variance_list[8] + cost_variance_list[9] + cost_variance_list[10])
    cost_variance_list.insert(15, cost_variance_list[12] + cost_variance_list[13] + cost_variance_list[14])
    cost_variance_list.append(cost_variance_list[3] + cost_variance_list[7] + cost_variance_list[11] + cost_variance_list[15])

    percent_variance_list.insert(3, 0)
    percent_variance_list.insert(7, 0)
    percent_variance_list.insert(11, 0)
    percent_variance_list.insert(15, 0)

    # get the proper variance% for q1, q2, q3, q4, and annual
    if benchmark_list[3] != 0:
        percent_variance_list[3] = ((actual_list[3]-benchmark_list[3])*1.0 / benchmark_list[3]) * 100
    if benchmark_list[7] != 0:
        percent_variance_list[7] = ((actual_list[7]-benchmark_list[7])*1.0 / benchmark_list[7]) * 100
    if benchmark_list[11] != 0:
        percent_variance_list[11] = ((actual_list[11]-benchmark_list[11])*1.0 / benchmark_list[11]) * 100
    if benchmark_list[15] != 0:
        percent_variance_list[15] = ((actual_list[15]-benchmark_list[15])*1.0 / benchmark_list[15]) * 100

    if benchmark_list[16] == 0:
        percent_variance_list.append(0)
    else:
        percent_variance_list.append(((actual_list[16]-benchmark_list[16])*1.0 / benchmark_list[16]) * 100)

    # round each list to the nearest integer
    utility_list = [int_round(x) for x in utility_list]
    actual_list = [int_round(x) for x in actual_list]
    benchmark_list = [int_round(x) for x in benchmark_list]
    plan_list = [int_round(x) for x in plan_list]

    y_unit_label = get_y_unit_label(y_units)
    return {"sitedata":[
        {"label": "Utility " + y_unit_label,
         "data": utility_list},
        {"label": "Actual " + y_unit_label,
         "data": actual_list},
        {"label": "Benchmark " + y_unit_label,
         "data": benchmark_list},
        {"label": "Plan " + y_unit_label,
         "data": plan_list},
        {"label": "Variance ($)",
         "data": cost_variance_list},
        {"label": "Variance (%)",
         "data": percent_variance_list}
    ]}

def get_first_account_for_group_of_type(group_id, account_type, uow):
    accounts = uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
    return accounts[0]


def get_component_point_conversion(from_unit, to_unit):
    factor = 1.0
    if from_unit == "kw":
        factor = 3412.14 / 4.0
    elif from_unit == "kwh":
        factor = 3412.14
    elif from_unit == "cf/hr":
        factor = 1023.0 / 4.0
    elif from_unit == "btuh":
        factor = 1.0 / 4.0
    elif from_unit == "hp":
        factor = 2544.43 / 4.0
    elif from_unit == "tons":
        factor = 12000.0 / 4.0
    elif from_unit == "cf":
        factor = 1023.0

    if to_unit == "kbtu":
        factor /= 1000.0
    elif to_unit == "mmbtu":
        factor /= 1000000.0

    return factor

def get_account_data_new(report, accounts_grouped, acc, config, g):
    """
    Gets the account energy record information
    :param report: the ConsumptionTextReport object that the data is being stored in
    :param accounts_grouped: distinct list of accounts for a given group
    :param account: the current account
    :param config: report configuration
    :param g:
    :return:
    """
    # initialize all values used per account
    report.account_utility = 0
    report.account_reported = 0
    report.account_benchmark = 0
    report.account_hours = 0
    report.account_reported_hours = 0
    report.account_price_normalization = 0
    report.account_benchmark_hours = 0
    report.account_cost_reduction = 0

    reported_cost = 0
    benchmark_cost = 0

    # set the locale
    locale.setlocale(locale.LC_ALL, '')

    # get the query entries for the account
    account = accounts_grouped[acc]
    report_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(account, group_by_account=True)

    # get the type of group to figure out the proper cost factor to use
    account_model = g.uow.accounts.get_by_id(acc)
    if account_model.type.lower() == 'electric':
        cost_unit_factor = get_factor('kwh', 'sum_btu')
    else:
        cost_unit_factor = get_factor('mcf', 'sum_btu')

    grouped = defaultdict(list)

    # group by each value returned from the query
    for d in report_data:
        grouped[d['group']['value']].append(d)

    # loop through all records returned from the query
    for value in grouped:
        entry = grouped[value]

        # handle same year in a simple way
        if config.report_year == config.benchmark_year:
            report_record_hours = entry[0]['reduction']['sum_hours_in_record']
            report_record_value = entry[0]['reduction'][report.y_unit_map] / report_record_hours

            # update report, utiltiy, and benchmark values
            report.account_utility += report_record_value

            report.account_reported += report_record_value
            report.account_reported_hours += report_record_hours

            report.account_benchmark += report_record_value
            report.account_benchmark_hours += benchmark_record_hours

        # search the entry for the report year and add data to the account utility
        for rec in entry:
            if rec['group']['year'] == config.report_year:
                report.account_utility += rec['reduction'][report.y_unit_map] / rec['reduction']['sum_hours_in_record']

        # if the data exists for both years
        if len(entry) > 1:
            benchmark_record = 0
            reported_avg_size = 0
            benchmark_avg_size = 0
            benchmark_record_hours = 0
            benchmark_record_btu_normalized = 0
            report_price_per_unit = 0
            for record in entry:
                if record['group']['year'] == config.report_year:
                    report_record_hours = record['reduction']['sum_hours_in_record']

                    report_record_value = record['reduction'][report.y_unit_map] * 1.0 / report_record_hours
                    reported_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / report_record_hours
                    report_price_per_unit = record['reduction']['sum_price_normalization'] * 1.0 / report_record_hours

                    reported_cost += (report_record_value * cost_unit_factor * report_price_per_unit)

                    # update the totals for the report year
                    report.account_reported += record['reduction'][report.y_unit_map] * 1.0 / report_record_hours
                    report.account_reported_hours += report_record_hours

                    # update the overall totals
                    report.account_price_normalization += record['reduction']['sum_price_normalization']
                elif record['group']['year'] == config.benchmark_year:
                    benchmark_record_hours = record['reduction']['sum_hours_in_record']

                    benchmark_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / benchmark_record_hours
                    benchmark_record_btu_normalized = record['reduction'][report.y_unit_map]

            # normalize the benchmark value
            size_ratio = reported_avg_size * 1.0 / benchmark_avg_size
            benchmark_record_btu_normalized *= size_ratio
            benchmark_record_btu_normalized /= benchmark_record_hours
            benchmark_cost += (benchmark_record_btu_normalized * cost_unit_factor * report_price_per_unit)

            # update the totals for the benchmark year
            report.account_benchmark += benchmark_record_btu_normalized
            report.account_benchmark_hours += benchmark_record_hours

    raw_data = {'account_name': account_model.name, 'utility': "{:,d}".format(int(report.account_utility)),
         'reported_utility': "{:,d}".format(int(report.account_reported)),
         'benchmark_utility': "{:,d}".format(int(report.account_benchmark)),
         'difference': "{:,d}".format(int(report.account_difference)),
         'change': "{:10.2f}%".format(report.account_change),
         'savings': locale.currency(report.account_cost_reduction)}
    print(raw_data)
    # get the data using the electic/gas unit factors
    if account_model.type.lower() == 'electric':
        report.account_utility *= report.electric_unit_factor
        report.account_reported *= report.electric_unit_factor
        report.account_benchmark *= report.electric_unit_factor
    else:
        print(report.gas_unit_factor)
        report.account_utility *= report.gas_unit_factor
        report.account_reported *= report.gas_unit_factor
        report.account_benchmark *= report.gas_unit_factor
    trace()
    # update the total hours
    report.account_hours += (report.account_benchmark_hours + report.account_reported_hours)

    report.account_difference = report.account_benchmark - report.account_reported

    # get cost reduction
    report.account_cost_reduction = benchmark_cost - reported_cost


    if report.account_benchmark == 0:
        report.account_change = 0
    else:
        report.account_change = (report.account_difference * 1.0 / report.account_benchmark) * 100

    # create a dictionary using the account's data to be used later on
    account_data = {'account_name': account_model.name, 'utility': "{:,d}".format(int(report.account_utility)),
         'reported_utility': "{:,d}".format(int(report.account_reported)),
         'benchmark_utility': "{:,d}".format(int(report.account_benchmark)),
         'difference': "{:,d}".format(int(report.account_difference)),
         'change': "{:10.2f}%".format(report.account_change),
         'savings': locale.currency(report.account_cost_reduction)}

    # get the data using the btu units
    get_btu_data_for_account(report, account_model, reported_cost, benchmark_cost)

    # create dictionary object to be used in the table
    btu_account_data = {'account_name': account_model.name,
                          'utility': "{:,d}".format(int(report.account_utility_btu)),
                          'reported_utility': "{:,d}".format(int(report.account_reported_btu)),
                          'benchmark_utility': "{:,d}".format(int(report.account_benchmark_btu)),
                          'difference': "{:,d}".format(int(report.account_difference_btu)),
                          'change': "{:10.2f}%".format(report.account_change_btu),
                          'savings': locale.currency(report.account_cost_reduction)}

    report.entity_all_account_data.append(btu_account_data)

    # add to totals
    if account_model.type.lower() == 'electric':
        # increase the group's electric account totals
        report.entity_electric_utility += report.account_utility
        report.entity_electric_reported += report.account_reported
        report.entity_electric_benchmark += report.account_benchmark
        report.entity_electric_price_normalization += report.account_price_normalization
        report.entity_electric_reported_hours += report.account_reported_hours
        report.entity_electric_benchmark_hours += report.account_benchmark_hours
        report.entity_electric_hours += report.account_hours
        report.entity_electric_cost_reduction += report.account_cost_reduction

        # add account data to the list of electric accounts for use in table
        report.entity_electric_account_data.append(account_data)
    else:
        # increase the group's gas account totals
        report.entity_gas_utility += report.account_utility
        report.entity_gas_benchmark += report.account_benchmark
        report.entity_gas_reported += report.account_reported
        report.entity_gas_price_normalization += report.account_price_normalization
        report.entity_gas_hours += report.account_hours
        report.entity_gas_reported_hours += report.account_reported_hours
        report.entity_gas_benchmark_hours += report.account_benchmark_hours
        report.entity_gas_cost_reduction += report.account_cost_reduction

        # add account data to the list of gas accounts for use in table
        report.entity_gas_account_data.append(account_data)

def get_group_data_new(report, group_id, config, g):
    group_name = g.uow.groups.get_group_by_id(group_id).name
    descendants = g.uow.groups.get_descendants(group_id)
    accounts = []

    # create lists to hold electric and gas values
    report.entity_electric_account_data = []
    report.entity_gas_account_data = []
    report.entity_all_account_data = []

    # initialize all running totals
    report.entity_electric_utility = 0
    report.entity_electric_reported = 0
    report.entity_electric_benchmark = 0
    report.entity_electric_hours = 0
    report.entity_electric_reported_hours = 0
    report.entity_electric_benchmark_hours = 0
    report.entity_electric_price_normalization = 0
    report.entity_electric_cost_reduction = 0
    report.entity_gas_utility = 0
    report.entity_gas_reported = 0
    report.entity_gas_benchmark = 0
    report.entity_gas_hours = 0
    report.entity_gas_reported_hours = 0
    report.entity_gas_benchmark_hours = 0
    report.entity_gas_price_normalization = 0
    report.entity_gas_cost_reduction = 0

    report.y_unit_map = 'sum_btu'
    report.electric_unit_factor = get_factor(config.electric_units, report.y_unit_map)
    report.gas_unit_factor = get_factor(config.gas_units, report.y_unit_map)
    report.btu_unit_factor = get_factor(config.btu_units, report.y_unit_map)

    # get the conversion factors from the electric/gas/btu unit factor to mmbtu
    report.electric_to_mmbtu_factor = 1 / report.electric_unit_factor * get_factor('mmbtus', report.y_unit_map)
    report.gas_to_mmbtu_factor = 1 / report.gas_unit_factor * get_factor('mmbtus', report.y_unit_map)
    report.btu_to_mmbtu_factor = 1 / report.btu_unit_factor * get_factor('mmbtus', report.y_unit_map)

    # set the locale
    locale.setlocale(locale.LC_ALL, '')

    # get all accounts for group and descendants
    for gr in descendants:
        acc_temp = get_accounts_for_group(gr['id'], config.account_type, config.report_year, config.comparison_type,
                                          config.demand_type, g)
        acc_temp += get_accounts_for_group(gr['id'], config.account_type, config.benchmark_year,
                                           config.comparison_type, config.demand_type, g)
        accounts += acc_temp

    if len(accounts) > 0:
        # get distinct list of account id's for the current group
        accounts_grouped = defaultdict(list)
        for a in accounts:
            accounts_grouped[a[0]].append(a)

        for a in accounts_grouped:
            get_account_data(report, accounts_grouped, a, config, g)

        # get difference, cost reduction, and change for the group electric and gas accounts
        report.entity_electric_difference = report.entity_electric_benchmark - report.entity_electric_reported
        report.entity_gas_difference = report.entity_gas_benchmark - report.entity_gas_reported

        if report.entity_electric_benchmark == 0:
            report.entity_electric_change = 0
        else:
            report.entity_electric_change = (report.entity_electric_difference * 1.0 / report.entity_electric_benchmark) * 100.0

        if report.entity_gas_benchmark == 0:
            report.entity_gas_change = 0
        else:
            report.entity_gas_change = (report.entity_gas_difference * 1.0 / report.entity_gas_benchmark) * 100

        # convert from electric and gas units to mmbtus
        report.entity_electric_utility_btu = report.entity_electric_utility / report.electric_unit_factor * report.btu_unit_factor
        report.entity_electric_reported_btu = report.entity_electric_reported / report.electric_unit_factor * report.btu_unit_factor
        report.entity_electric_benchmark_btu = report.entity_electric_benchmark / report.electric_unit_factor * report.btu_unit_factor

        report.entity_gas_utility_btu = report.entity_gas_utility / report.gas_unit_factor * report.btu_unit_factor
        report.entity_gas_reported_btu = report.entity_gas_reported / report.gas_unit_factor * report.btu_unit_factor
        report.entity_gas_benchmark_btu = report.entity_gas_benchmark / report.gas_unit_factor * report.btu_unit_factor

        # find values for all accounts by summing the electric and gas account running totals
        report.entity_all_utility = report.entity_electric_utility_btu + report.entity_gas_utility_btu
        report.entity_all_reported = report.entity_electric_reported_btu + report.entity_gas_reported_btu
        report.entity_all_benchmark = report.entity_electric_benchmark_btu + report.entity_gas_benchmark_btu
        report.entity_all_price_normalization = report.entity_electric_price_normalization + report.entity_gas_price_normalization
        report.entity_all_hours = report.entity_electric_hours + report.entity_gas_hours
        report.entity_all_benchmark_hours = report.entity_electric_benchmark_hours + report.entity_gas_benchmark_hours
        report.entity_all_reported_hours = report.entity_electric_reported_hours + report.entity_gas_reported_hours
        report.entity_all_cost_reduction = report.entity_electric_cost_reduction + report.entity_gas_cost_reduction

        if report.entity_all_benchmark_hours == 0:
            report.entity_all_benchmark = 0
        else:
            report.entity_all_benchmark = report.entity_all_benchmark * (report.entity_all_reported_hours * 1.0 / report.entity_all_benchmark_hours)

        # get difference, cost reduction, and change for all of the accounts
        report.entity_all_difference = report.entity_all_benchmark - report.entity_all_reported

        if report.entity_all_benchmark == 0:
            report.entity_all_change = 0
        else:
            report.entity_all_change = (report.entity_all_difference * 1.0 / report.entity_all_benchmark) * 100

        report.grand_total_utility += report.entity_all_utility
        report.grand_total_reported += report.entity_all_reported
        report.grand_total_benchmark += report.entity_all_benchmark
        report.grand_total_hours += report.entity_all_hours
        report.grand_total_reported_hours += report.entity_all_reported_hours
        report.grand_total_benchmark_hours += report.entity_all_benchmark_hours
        report.grand_total_price_normalization += report.entity_all_price_normalization
        report.grand_total_cost_reduction += report.entity_all_cost_reduction
    print(report.grand_total_cost_reduction)



