from collections import defaultdict
from copy import deepcopy
import json
from operator import itemgetter
from time import strptime
import itertools
import math
from pdb import set_trace as trace

import locale
from flask import g, session, abort
from api.models.ReportingConfiguration import ReportingConfiguration
from api.models.ReportChartInformation import ReportChartInformation
from api.models.TotalEnergyData import TotalEnergyData
from api.models.ConsumptionTextReport import  ConsumptionTextReport
from api.models.TotalEnergyDataContainer import TotalEnergyDataContainer
from extensions.binding import from_request_body, require_permissions, require_any_permission
from flask import Blueprint, send_file
from flask.ext.login import login_required
from pdfgenerator.DataReports import DataReports
from reporting import SharedReporting


ReportingGroupsBlueprint = Blueprint("ReportingGroupsBlueprint", __name__)

@ReportingGroupsBlueprint.route("/api/ReportingGroups/GetIntensityData", methods=["POST"])
@from_request_body("config", ReportingConfiguration)
@require_permissions(['Run Group Reports'])
def get_intensity_report(config):

    intensity_chart_info = get_intensity_chart_data(config.entity_ids, config.account_type, config.report_year,
                                                    config.comparison_type, config.demand_type, g)

    return json.dumps(intensity_chart_info.__dict__)


# Main function that is called when the export to pdf button is pressed
@ReportingGroupsBlueprint.route("/api/ReportingGroups/GetReport", methods=["POST"])
@login_required
@from_request_body("config", ReportingConfiguration)
def get_report(config):
    report_name = "DefaultReportName"
    report_path = ""

    # make sure submitted_to isn't empty
    if not config.submitted_to:
        return abort(400)

    submitted_by_user = g.uow.users.get_user_by_id(session["current_user"]['id'])
    submitted_to = config.submitted_to
    # get the submitted by and submitted to
    submitted_by_user, submitted_to = SharedReporting.get_submitted_contacts(submitted_by_user, submitted_to, g)

    total_energy_chart_info = TotalEnergyDataContainer()

    # determine the x units
    x_units = "F"
    total_energy_chart_info.x_axis_label = "Temperature (" + x_units + ")"
    if config.comparison_type == "dewpt":
        x_units = "Dewpt"
        total_energy_chart_info.x_axis_label = "Dewpt"
    elif config.comparison_type == "enthalpy":
        x_units = "Enthalpy"
        total_energy_chart_info.x_axis_label = "Enthalpy"

    # get actual y units to send back, and get their equivalent column in the database
    # then call the proper report function determined by config.report_type
    if config.report_type == "consumption":
        report_name = "Consumption_Report"
        if config.account_type == "electric":
            y_units = config.electric_units
            y_unit_map = 'sum_btu'
            total_energy_chart_info.title = "Total Energy Usage - Electric"
        elif config.account_type == "gas":
            y_units = config.gas_units
            y_unit_map = 'sum_btu'
            total_energy_chart_info.title = "Total Energy Usage - Gas"
        else:
            y_units = config.btu_units
            y_unit_map = "sum_btu"
            total_energy_chart_info.title = "Total Energy Usage"
        total_energy_chart_info.y_axis_label = "Average Energy Usage (" + SharedReporting.get_y_unit_label(y_units) + ")"

        # Generate consumption report with data
        report_path = generate_consumption_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g)
    elif config.report_type == "text":
        report_name = "Consumption Text Report"
        report_path = generate_consumptiontext_report(config, submitted_by_user, g)
    elif config.report_type == "kvar":
        report_name = "kVarh"
        y_units = "kvar"
        y_unit_map = "sum_kvar"
        total_energy_chart_info.y_axis_label = "Average Electric Usage (kVar)"
        total_energy_chart_info.title = "kVar"
        report_path = generate_kvarh_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g)
    elif config.report_type == "kva":
        report_name = "kVah"
        y_units = "kva"
        y_unit_map = "kva"
        total_energy_chart_info.y_axis_label = "Average Electric Usage (kVa)"
        total_energy_chart_info.title = "kVa"
        report_path = generate_kvah_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g)
    elif config.report_type == "powerfactor":
        report_name = "Power Factor"
        y_units = "pf"
        y_unit_map = "pf"
        total_energy_chart_info.y_axis_label = "Average Power Factor"
        total_energy_chart_info.title = "Power Factor"
        report_path = generate_powerfactor_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g)
    elif config.report_type == "peak":
        report_name = "Peak Report"
        report_path = generate_peak_report(config, submitted_by_user, submitted_to, g)
    elif config.report_type == "variance":
        report_name = "Variance Report"
        if config.account_type == "electric":
            y_units = config.electric_units
        elif config.account_type == "gas":
            y_units = config.gas_units
        else:
            y_units = config.btu_units
        y_unit_map = "sum_btu"
        report_path = generate_variance_report(config, y_units, y_unit_map, submitted_by_user, submitted_to, g)

    # send file back out to user for download
    return send_file(report_path, mimetype='application/pdf', as_attachment=True, attachment_filename=report_name + '.pdf')


# Gathers data for the consumption report and generate its pdf
def generate_consumption_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g):

    # collect information for the intensity chart
    intensity_chart_info = get_intensity_chart_data(config.entity_ids, config.account_type, config.report_year, config.comparison_type, config.demand_type, g)

    year_group_grouping = {}
    # loop through every group id in the configuration and get their consumption chart data
    for group_id in config.entity_ids:
        # get the group and descendants
        group = g.uow.groups.get_group_by_id(group_id)
        descendants = g.uow.groups.get_descendants(group_id)

        accounts = []
        # get all of the accounts for the given group id's descendants
        for gr in descendants:
            accounts += SharedReporting.get_accounts_for_group(gr['id'], config.account_type, config.report_year, config.comparison_type,
                                               config.demand_type, g)

        # Get data associated with each account
        data = SharedReporting.get_total_energy_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type, y_units, y_unit_map, g)
        total_energy_chart_info.data.append({'entity': group.name, 'data': data['chart_data']})

        for year in data['year_data']:
            # check if the year has been added to the grouping before
            if not year in year_group_grouping:
                # the year hasn't been added to the grouping, so just create a new entry in dictionary
                year_group_grouping[year] = [{'entity': group.name + " (" + str(year) + ")",
                                             'data': data['year_data'][year]}]
            else:
                # the year has been added to the grouping before, so we append the new entry
                year_group_grouping[year].append({'entity': group.name + " (" + str(year) + ")",
                                                  'data': data['year_data'][year]})

    # Generate consumption report with data
    report_path = DataReports.generate_consumption_report(config.report_year, config.benchmark_year,
                                                          intensity_chart_info, total_energy_chart_info,
                                                          year_group_grouping, submitted_by_user, submitted_to,
                                                          SharedReporting.get_y_unit_label(y_units))
    return report_path


# Gathers data for the consumption text report and generate its pdf
def generate_consumptiontext_report(config, submitted_by_user, g):
    # Generate consumption text report with data
    report_path = DataReports.generate_consumptiontext_report(config.report_year, config.benchmark_year, SharedReporting.generate_consumptiontext_report(config, 'groups', g), submitted_by_user, config.account_type)
    return report_path


# Gathers data for the kva report and generate its pdf
def generate_kvah_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g):
    for group_id in config.entity_ids:
        group = g.uow.groups.get_group_by_id(group_id)
        # Get data associated with each account
        accounts = []
        descendants = g.uow.groups.get_descendants(group_id)

        # Get all accounts for each group for the desired year
        for gr in descendants:
            accounts += SharedReporting.get_accounts_for_group(gr['id'], 'electric', config.report_year, config.comparison_type, config.demand_type, g)

        # Get data associated with each account
        data = SharedReporting.get_total_energy_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type, y_units, y_unit_map, g)
        total_energy_chart_info.data.append({'entity': group.name, 'data': data})

    # Generate consumption report with data
    report_path = DataReports.generate_kvah_report(config.report_year, config.benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to)
    return report_path


# Gathers data for the kvar report and generate its pdf
def generate_kvarh_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g):
    for group_id in config.entity_ids:
        group = g.uow.groups.get_group_by_id(group_id)
        # Get data associated with each account
        accounts = []
        descendants = g.uow.groups.get_descendants(group_id)
        for gr in descendants:
            accounts += SharedReporting.get_accounts_for_group(gr['id'], 'electric', config.report_year, config.comparison_type, config.demand_type, g)
        data = SharedReporting.get_total_energy_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type, y_units, y_unit_map, g)
        total_energy_chart_info.data.append({'entity': group.name, 'data': data})

    # Generate consumption report with data
    report_path = DataReports.generate_kvarh_report(config.report_year, config.benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to)
    return report_path


# Gathers data for the power factor report and generate its pdf
def generate_powerfactor_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g):
    for group_id in config.entity_ids:
        group = g.uow.groups.get_group_by_id(group_id)
        descendants = g.uow.groups.get_descendants(group_id)
        accounts = []
        # Get all accounts for each group for the desired year
        for gr in descendants:
            accounts += SharedReporting.get_accounts_for_group(gr['id'], 'electric', config.report_year, config.comparison_type, config.demand_type, g)

        # Get data associated with each account
        data = SharedReporting.get_pf_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type, g)
        total_energy_chart_info.data.append({'entity': group.name, 'data': data})

    # Generate consumption report with data
    report_path = DataReports.generate_powerfactor_report(config.report_year, config.benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to)
    return report_path


def generate_peak_report(config, submitted_by_user, submitted_to, g):
    """
    Gathers data for the peak report and generates a pdf
    :param config:
    :param g:
    :return:
    """

    data = get_peak_report_data(config, g)

    # generate peak report with data
    report_path = DataReports.generate_peak_report(data, config.report_year, submitted_by_user, submitted_to)
    return report_path


def generate_variance_report(config, y_units, y_unit_map, submitted_by_user, submitted_to, g):
    total_data = []
    for gr in config.entity_ids:
        group = g.uow.groups.get_group_by_id(gr)
        descendants = g.uow.groups.get_descendants(gr)
        accounts = []

        # check to make sure we should get electric accounts
        if config.account_type.lower() != 'gas':
            # get all electric accounts
            for desc in descendants:
                accounts += SharedReporting.get_accounts_for_group(desc['id'], 'electric', config.report_year, config.comparison_type, config.demand_type, g)
                accounts += SharedReporting.get_accounts_for_group(desc['id'], 'electric', config.benchmark_year, config.comparison_type, config.demand_type, g)

            # get all month utility, actual, benchmark, plan, variance ($), and variance (%) for every month in the report year
            electric_data = SharedReporting.get_variance_report_data(accounts, 'electric', config.report_year, config.benchmark_year, config.demand_type, y_units, y_unit_map, g)
        else:
            # create blank template so no null errors are thrown later
            electric_data = {"sitedata": [
                {"label": "",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "Variance ($)",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "Variance (%)",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
            ]}

        accounts = []
        if config.account_type.lower() != 'electric':
            # get all gas accounts
            for desc in descendants:
                accounts += SharedReporting.get_accounts_for_group(desc['id'], 'gas', config.report_year, config.comparison_type, config.demand_type, g)
                accounts += SharedReporting.get_accounts_for_group(desc['id'], 'gas', config.benchmark_year, config.comparison_type, config.demand_type, g)

            # get gas data
            gas_data = SharedReporting.get_variance_report_data(accounts, 'gas', config.report_year, config.benchmark_year, config.demand_type, y_units, y_unit_map, g)
        else:
            # create blank template so no null errors are thrown later
            gas_data = {"sitedata": [
                {"label": "",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "Variance ($)",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},
                {"label": "Variance (%)",
                 "data": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
            ]}

        data = {"entity_name": group.name, "sitedata": [
            {"label": "",
             "data": []},
            {"label": "",
             "data": []},
            {"label": "",
             "data": []},
            {"label": "",
             "data": []},
            {"label": "Variance ($)",
             "data": []},
            {"label": "Variance (%)",
             "data": []}
        ]}

        # determine which site labels to use
        if config.account_type.lower() != 'electric':
            labels = [gas_data["sitedata"][0]["label"], gas_data["sitedata"][1]["label"], gas_data["sitedata"][2]["label"], gas_data["sitedata"][3]["label"]]
        else:
            labels = [electric_data["sitedata"][0]["label"], electric_data["sitedata"][1]["label"], electric_data["sitedata"][2]["label"], electric_data["sitedata"][3]["label"]]

        data["sitedata"][0]["label"] = labels[0]
        data["sitedata"][1]["label"] = labels[1]
        data["sitedata"][2]["label"] = labels[2]
        data["sitedata"][3]["label"] = labels[3]

        # add gas data to electric data
        utility_list = [a+b for a,b in zip(electric_data["sitedata"][0]["data"], gas_data["sitedata"][0]["data"])]
        actual_list = [a+b for a,b in zip(electric_data["sitedata"][1]["data"], gas_data["sitedata"][1]["data"])]
        benchmark_list = [a+b for a,b in zip(electric_data["sitedata"][2]["data"], gas_data["sitedata"][2]["data"])]
        plan_list = [a+b for a,b in zip(electric_data["sitedata"][3]["data"], gas_data["sitedata"][3]["data"])]
        cost_variance_list = [a+b for a,b in zip(electric_data["sitedata"][4]["data"], gas_data["sitedata"][4]["data"])]
        percent_variance_list = [a+b for a,b in zip(electric_data["sitedata"][5]["data"], gas_data["sitedata"][5]["data"])]

        # format all data to be used in the javascript
        utility_list = ["{:,d}".format(entry) for entry in utility_list]
        actual_list = ["{:,d}".format(entry) for entry in actual_list]
        benchmark_list = ["{:,d}".format(entry) for entry in benchmark_list]
        plan_list = ["{:,d}".format(entry) for entry in plan_list]
        percent_variance_list = ["{:,.2f}%".format(entry) for entry in percent_variance_list]

        locale.setlocale(locale.LC_ALL, '')
        cost_variance_list = [locale.currency(entry, grouping=True) for entry in cost_variance_list]

        # set the final data values
        data["entity_name"] = group.name
        data["sitedata"][0]["data"] = utility_list
        data["sitedata"][1]["data"] = actual_list
        data["sitedata"][2]["data"] = benchmark_list
        data["sitedata"][3]["data"] = plan_list
        data["sitedata"][4]["data"] = cost_variance_list
        data["sitedata"][5]["data"] = percent_variance_list
        total_data.append(data)
    report_path = DataReports.generate_variance_report(total_data, config.report_year, config.benchmark_year, submitted_by_user, submitted_to)
    return report_path


def get_intensity_chart_data(group_ids, account_type, report_year, comparison_type, demand_type, g):
    # Set x units for the intensity chart on the consumption report
    x_units = "F"
    x_axis_label = "Temperature (" + x_units + ")"
    if comparison_type == "enthalpy":
        x_axis_label = "Enthalpy"
    elif comparison_type == "dewpt":
        x_axis_label = "Dewpoint"

    accounts = []
    final_data = []

    # get all accounts for group and it's descendants
    for gr in group_ids:
        data_insert = []
        accounts = []
        group = g.uow.groups.get_group_by_id(gr).name
        descendants = g.uow.groups.get_descendants(gr)
        for desc in descendants:
            accounts += SharedReporting.get_accounts_for_group(desc['id'], account_type, report_year, comparison_type, demand_type, g)

        consider_demand_type = False
        if demand_type != 'all':
            consider_demand_type = True

        if len(accounts) > 0:
            # Get data for the consumption report
            intensity_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(accounts, consider_demand_type=consider_demand_type)
        else:
            intensity_data = []

        # loop through and adjust the values based on size normalization
        for entry in intensity_data:
            data_insert.append([entry['group']['value'],
                               entry['reduction']['sum_btu'] / entry['reduction']['sum_size_normalization']])

        # add to the final data
        final_data.append({"name": group, 'data':data_insert})

    # Set metadata for consumption report
    intensity_chart_info = ReportChartInformation()
    intensity_chart_info.title = "Intensity"
    intensity_chart_info.y_axis_label = "Energy Intensity (BTU/sqft)"
    intensity_chart_info.x_axis_label = x_axis_label
    intensity_chart_info.data = final_data
    return intensity_chart_info


def get_pf_chart_data_web(group_id, report_year, benchmark_year, comparison_type, demand_type, g):
    """
    Gets and calculates all data needed for power factor charts
    :param group_id: group id that is being reported on
    :param report_year: report year
    :param benchmark_year: benchmark year
    :param demand_type: 'all'/'peak'/'offpeak'
    :param g:
    :return: data
    """

    data_list = []

    group = g.uow.groups.get_group_by_id(group_id)
    descendants = g.uow.groups.get_descendants(group_id)
    accounts = []
    # Get all accounts for each group for the desired year
    for gr in descendants:
        accounts += SharedReporting.get_accounts_for_group(gr['id'], 'electric', report_year, comparison_type, demand_type, g)
        accounts += SharedReporting.get_accounts_for_group(gr['id'], 'electric', benchmark_year, comparison_type, demand_type, g)
    # get the benchmark data for the accounts to avoid having to do it again later
    report_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(accounts, data_field_name='sum_kvar')

    # create a copy of the benchmark records
    account_group = defaultdict(list)
    for d in report_data:
        account_group[d['group']['value']].append(d)

    calculated_totals = SharedReporting.calculate_pf_data(account_group, report_year, benchmark_year, report_year == benchmark_year)

    return calculated_totals


def get_total_energy_chart_data_web(group_id, report_year, benchmark_year, account_type, comparison_type, demand_type, y_units, y_unit_map, g):
    # determine if demand will be included in query
    if demand_type != 'all':
        consider_demand_type = True
    else:
        consider_demand_type = False

    same_year = report_year == benchmark_year
    # get unit factor for the selected y units
    unit_factor = SharedReporting.get_factor(y_units, y_unit_map)

    if account_type == "all":
        unit_factor *= 2.0

    data = TotalEnergyData()

    # get all descendants of group
    descendants = g.uow.groups.get_descendants(group_id)
    accounts = []

    # Get all accounts for each group for the desired year
    for gr in descendants:
        accounts += SharedReporting.get_accounts_for_group(gr['id'], account_type, report_year, comparison_type,
                                                           demand_type, g)
        if not same_year:
            accounts += SharedReporting.get_accounts_for_group(gr['id'], account_type, benchmark_year, comparison_type,
                                                               demand_type, g)

    if len(accounts) < 1:
        benchmark_data = []
    else:
        benchmark_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(accounts, data_field_name=y_unit_map, consider_demand_type=consider_demand_type)

    # group the data by value
    grouped = defaultdict(list)

    for d in benchmark_data:
        grouped[d['group']['value']].append(d)

    reported_consumption = []
    diff = []
    benchmark_diff = []
    benchmark_consumption = []

    # get the distinct values for the group
    grouped_keys = list(grouped.keys())
    grouped_keys.sort()

    # if the report year and benchmark year are the same, it will be handled differently
    if same_year:
        for value in grouped_keys:
            entry = grouped[value]
            record_value = entry[0]['reduction'][y_unit_map] * unit_factor / entry[0]['reduction']['sum_hours_in_record']
            reported_consumption.append([value, round(record_value, 5)])
            diff.append([value, 0])
            benchmark_consumption.append([value, round(record_value, 5)])
            benchmark_diff.append([value, 0])
    else:
        # loop through every distinct value and get all of the records for it
        for value in grouped_keys:
            entry = grouped[value]
            if len(entry) > 1:
                report_record = 0
                benchmark_record = 0
                report_avg_size = 0
                benchmark_avg_size = 0
                benchmark_record_hours = 0
                for record in entry:
                    if record['group']['year'] == report_year:
                        report_record_hours = record['reduction']['sum_hours_in_record']

                        # normalize the values
                        report_record = round(record['reduction'][y_unit_map] * unit_factor / report_record_hours, 5)
                        reported_consumption.append([value, report_record])

                        report_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / report_record_hours
                    elif record['group']['year'] == benchmark_year:
                        benchmark_record_hours = record['reduction']['sum_hours_in_record']

                        # get the size and record value to be normalized later
                        benchmark_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / benchmark_record_hours
                        benchmark_record = record['reduction'][y_unit_map] * unit_factor

                # normalize the benchmark value
                size_ratio = report_avg_size * 1.0 / benchmark_avg_size
                benchmark_record *= size_ratio
                benchmark_record /= benchmark_record_hours

                # add normalized value to charts
                benchmark_consumption.append([value, round(benchmark_record, 5)])
                benchmark_diff.append([value, 0])
                diff.append([value, benchmark_record - report_record])

    data.reported_consumption = reported_consumption
    data.benchmark_consumption = benchmark_consumption
    data.diff = diff
    data.benchmark_diff = benchmark_diff
    return data


# Gets accounts for a group. These can be filtered down by gas/electric accounts
def get_accounts_for_group(group_id, account_type, report_year, comparison_type, demand_type):
    accounts = []
    if demand_type != 'all':
        if account_type != 'all':
            all_accounts_with_type = g.uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
            if all_accounts_with_type:
                for acc in all_accounts_with_type:
                    accounts.append([acc['id'], comparison_type, report_year, demand_type])
        else:
            for account in g.uow.accounts.get_all_for_group(group_id):
                accounts.append([account['id'], comparison_type, report_year, demand_type])
    else:
        if account_type != 'all':
            all_accounts_with_type = g.uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
            if all_accounts_with_type:
                for acc in all_accounts_with_type:
                    accounts.append([acc['id'], comparison_type, report_year])
        else:
            for account in g.uow.accounts.get_all_for_group(group_id):
                accounts.append([account['id'], comparison_type, report_year])
    return accounts

@ReportingGroupsBlueprint.route("/api/ReportingGroups/GetTotalEnergyData", methods=["POST"])
@from_request_body("config", ReportingConfiguration)
@require_any_permission(['Run Group Reports', 'View Dashboard'])
def get_total_energy_data(config):

    # determine the x units
    x_units = "F"
    x_axis_label = "Temperature (" + x_units + ")"
    if config.comparison_type == "dewpt":
        x_units = "Dewpt"
        x_axis_label = "Dewpt"
    elif config.comparison_type == "enthalpy":
        x_units = "Enthalpy"
        x_axis_label = "Enthalpy"

    # get actual y units to send back, and get their equivalent column in the database
    if config.report_type == "consumption":
        if config.account_type.lower() == "electric":
            y_units = config.electric_units
            y_unit_map = 'sum_btu'
            title = "Total Energy Usage - Electric"
        elif config.account_type.lower() == "gas":
            y_units = config.gas_units
            y_unit_map = 'sum_btu'
            title = "Total Energy Usage - Gas"
        else:
            y_units = config.btu_units
            y_unit_map = "sum_btu"
            title = "Total Energy Usage"
        y_axis_label = "Average Energy Usage (" + SharedReporting.get_y_unit_label(y_units) + ")"
    elif config.report_type == "kvar":
        y_units = "kvar"
        y_unit_map = "sum_kvar"
        y_axis_label = "Average Electric Usage (kVar)"
        title = "kVar"
    elif config.report_type == "kva":
        y_units = "kva"
        y_unit_map = "kva"
        y_axis_label = "Average Electric Usage (kVa)"
        title = "kVa"
    elif config.report_type == "powerfactor":
        y_units = "pf"
        y_unit_map = "pf"
        y_axis_label = "Average Power Factor"
        title = "Power Factor"
    else:  # this should never happen, but to prevent warnings we will set a value
        abort(409)

    if len(config.entity_ids) < 1 or config.entity_ids[0] is None:
        return_obj = [
            {
                'consumption-chart': [
                    {
                        'name': 'Reported Consumption',
                        'data': []
                    },
                    {
                        'name': 'Benchmark Consumption',
                        'data': []
                    }
                ],
                'difference-chart': [
                    {
                        'name': 'Reported Consumption',
                        'data': []
                    },
                    {
                        'name': 'Benchmark Consumption',
                        'data': []
                    }
                ],
                'yunits': y_units,
                'y_axis_label': y_axis_label,
                'xunits': x_units,
                'x_axis_label': x_axis_label,
                'title': title
            }
        ]
        return json.dumps(return_obj)

    # check to see if config is asking for a powerfactor report, as it requires a different function
    if config.report_type == "powerfactor":
        data = get_pf_chart_data_web(config.entity_ids[0], config.report_year, config.benchmark_year, config.comparison_type, config.demand_type, g)
    else:
        # we only care about the first group id since the configuration is being formatted before the request, as [group_id]
        data = get_total_energy_chart_data_web(config.entity_ids[0], config.report_year, config.benchmark_year,
                                               config.account_type, config.comparison_type, config.demand_type,
                                               y_units, y_unit_map, g)

    return_obj = [
        {
            'consumption-chart': [
                {
                    'name': 'Reported Consumption',
                    'data': data.reported_consumption
                },
                {
                    'name': 'Benchmark Consumption',
                    'data': data.benchmark_consumption
                }
            ],
            'difference-chart': [
                {
                    'name': 'Reported Consumption',
                    'data': data.diff
                },
                {
                    'name': 'Benchmark Consumption',
                    'data': data.benchmark_diff
                }
            ],
            'yunits': y_units,
            'y_axis_label': y_axis_label,
            'xunits': x_units,
            'x_axis_label': x_axis_label,
            'title': title
        }
    ]
    return json.dumps(return_obj)


@ReportingGroupsBlueprint.route("/api/ReportingGroups/GetBenchmarkPerformanceData", methods=["POST"])
@from_request_body("config", ReportingConfiguration)
@login_required
@require_any_permission(['Run Group Reports', 'View Dashboard'])
def get_benchmark_performance_data(config):
    final_data = []
    total_reported_utility = 0
    total_reported_size_normalization = 0
    total_reported_price_normalization = 0
    total_benchmark_utility = 0
    total_benchmark_size_normalization = 0
    total_benchmark_price_normalization = 0
    if len(config.entity_ids) < 1 or config.entity_ids[0] is None:
        return json.dumps({'group_data': [], 'total_reported_utility': "0",
                           'total_benchmark_utility': "0",
                           'total_performance': "0.00",
                           'total_difference': "0",
                           'total_variance': "0"})
    descendants = g.uow.groups.get_descendants(config.entity_ids[0])
    for d in descendants:
        reported_utility = 0
        reported_size_normalization = 0
        reported_price_normalization = 0
        benchmark_utility = 0
        benchmark_utility_list = []
        benchmark_size_normalization = 0
        benchmark_price_normalization = 0
        accounts = SharedReporting.get_accounts_for_group(d['id'], config.account_type, config.report_year, config.comparison_type,
                                          config.demand_type, g)
        accounts += SharedReporting.get_accounts_for_group(d['id'], config.account_type, config.benchmark_year, config.comparison_type,
                                           config.demand_type, g)
        if len(accounts) > 1:

            data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(accounts, None,
                                                                                                  consider_demand_type=False,
                                                                                                  group_by_account=True)
        else:
            data = []

        grouped = defaultdict(list)

        for de in data:
            grouped[de['group']['value']].append(de)

        for value in grouped:
            entry = grouped[value]
            if len(entry) > 1:
                for record in entry:
                    if record['group']['year'] == config.report_year:
                        reported_utility += record['reduction']['sum_btu']
                        reported_price_normalization += record['reduction']['sum_price_normalization']
                        reported_size_normalization += record['reduction']['sum_size_normalization']
                    elif record['group']['year'] == config.benchmark_year:
                        benchmark_utility_list.append(record['reduction']['sum_btu'])
                        benchmark_price_normalization += record['reduction']['sum_price_normalization']
                        benchmark_size_normalization += record['reduction']['sum_size_normalization']

        for entry in benchmark_utility_list:
            benchmark_utility += (float(reported_size_normalization) / benchmark_size_normalization) * entry

        total_reported_utility += reported_utility
        total_reported_price_normalization += reported_price_normalization
        total_reported_size_normalization += reported_size_normalization
        total_benchmark_utility += benchmark_utility
        total_benchmark_price_normalization += benchmark_price_normalization
        total_benchmark_size_normalization += benchmark_size_normalization

        difference = benchmark_utility - reported_utility

        if benchmark_utility == 0:
            performance = 0.0
        else:
            performance = ((benchmark_utility - reported_utility) / benchmark_utility) * 100.0

        final_data.append({'name': d['name'], 'performance': "{:10.2f}%".format(performance),
                           'benchmark': "{:,d}".format(int(benchmark_utility)),
                           'actual': "{:,d}".format(int(reported_utility)),
                           'difference': "{:,d}".format(int(difference)), 'variance': "${:,.2f}".format(
            reported_price_normalization * (benchmark_utility - reported_utility))})

    if total_benchmark_utility == 0:
        total_change = 0.0
    else:
        total_change = ((total_benchmark_utility - total_reported_utility) / total_benchmark_utility) * 100.0

    return json.dumps({'group_data': final_data, 'total_reported_utility': "{:,d}".format(int(total_reported_utility)),
                       'total_benchmark_utility': "{:,d}".format(int(total_benchmark_utility)),
                       'total_performance': "{:10.2f}".format(total_change),
                       'total_difference': "{:,d}".format(int(total_benchmark_utility - total_reported_utility)),
                       'total_variance': "${:,.2f}".format(
                           total_reported_price_normalization * (total_benchmark_utility - total_reported_utility))})


@ReportingGroupsBlueprint.route("/api/ReportingGroups/GetBenchmarkBudgetVarianceData", methods=['POST'])
@from_request_body("config", ReportingConfiguration)
@login_required
@require_permissions(['View Dashboard'])
def get_benchmark_budget_variance_data(config):
    """
    Returns data for the benchmark budget variance table shown on the dashboard.
    IMPORTANT: The Annual Budget column is not normalized to report year values, but everything else is.
    :param config:
    :return:
    """
    final_data = []
    # make sure they have a group selected
    if len(config.entity_ids) < 1 or config.entity_ids[0] is None:
        return json.dumps(final_data)

    # get the unit factor to change btu to mmbtu
    mmbtu_unit_factor = SharedReporting.get_factor('mmbtus', 'sum_btu')

    descendants = g.uow.groups.get_descendants(config.entity_ids[0])
    for d in descendants:
        accounts = SharedReporting.get_accounts_for_group(d['id'], config.account_type, config.report_year, config.comparison_type,
                                          config.demand_type, g)
        accounts += SharedReporting.get_accounts_for_group(d['id'], config.account_type, config.benchmark_year, config.comparison_type,
                                           config.demand_type, g)
        if len(accounts) > 1:
            data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(accounts, None,
                                                                                                  consider_demand_type=False,
                                                                                                  group_by_account=True)
        else:
            data = []

        account_group = defaultdict(list)

        for a in data:
            account_group[a['group']['account_id']].append(a)

        # gather data for each account
        for account_id in account_group:
            # get the data into a defaultdict to make sure we have records for both years
            data_dict = defaultdict(list)
            for e in account_group[account_id]:
                data_dict[e['group']['value']].append(e)

            # determine cost factor based on account type
            account_model = g.uow.accounts.get_by_id(account_id)
            if account_model.type.lower() == 'electric':
                cost_unit_factor = SharedReporting.get_factor('kwh', 'sum_btu')
            else:
                cost_unit_factor = SharedReporting.get_factor('mcf', 'sum_btu')

            reported_cost = 0
            reported_total = 0
            benchmark_cost = 0
            benchmark_total = 0
            benchmark_normalized_cost = 0

            # loop through data_dict and for each entry that has multiple years add it to the respective values
            for value in data_dict:
                entry = data_dict[value]
                # check if data exists for multiple years (report and benchmark)
                if len(entry) > 1:
                    benchmark_record = 0
                    reported_avg_size = 0
                    benchmark_avg_size = 0
                    benchmark_record_btu_normalized = 0
                    report_price_per_unit = 0
                    for record in entry:
                        if record['group']['year'] == config.report_year:
                            report_record_hours = record['reduction']['sum_hours_in_record']
                            report_record_price_norm = record['reduction']['sum_price_normalization']

                            # get necessary information to add to totals
                            report_record = record['reduction']['sum_btu'] * mmbtu_unit_factor
                            reported_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / report_record_hours
                            report_price_per_unit = report_record_price_norm * 1.0 / report_record_hours

                            # update totals
                            reported_cost += (record['reduction']['sum_btu'] * cost_unit_factor * report_price_per_unit)
                            reported_total += report_record
                        elif record['group']['year'] == config.benchmark_year:
                            benchmark_record_hours = record['reduction']['sum_hours_in_record']

                            benchmark_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / benchmark_record_hours
                            benchmark_record_btu_normalized = record['reduction']['sum_btu']
                            benchmark_record = record['reduction']['sum_btu'] * mmbtu_unit_factor

                            benchmark_price_per_unit = record['reduction']['sum_price_normalization'] * 1.0 / benchmark_record_hours
                            benchmark_cost += (record['reduction']['sum_btu'] * cost_unit_factor * benchmark_price_per_unit)

                    # get the adjusted benchmark value to be more accurate about consumption and prices
                    size_ratio = reported_avg_size * 1.0 / benchmark_avg_size
                    benchmark_record *= size_ratio

                    # normalize the btu value for proper cost calculation
                    benchmark_record_btu_normalized *= size_ratio
                    benchmark_normalized_cost += (benchmark_record_btu_normalized * cost_unit_factor * report_price_per_unit)

                    # update the benchmark total
                    benchmark_total += benchmark_record

            # calculate difference and variance
            difference = benchmark_total - reported_total

            if benchmark_total == 0:
                variance = 0
            else:
                variance = (difference * 1.0 / benchmark_total) * 100.0

            final_data.append({'name': g.uow.accounts.get_by_id(account_id).name,
                               'annual_budget': "${:,.2f}".format(benchmark_cost),
                               'consumption': "{:,d}".format(int(reported_total)),
                               'variance': "{:.1f}%".format(variance),
                               'budget_variance': "${:,.2f}".format(benchmark_normalized_cost - reported_cost)})
    return json.dumps(final_data)

@ReportingGroupsBlueprint.route("/api/ReportingGroups/peak", methods=["POST"])
@from_request_body("config", ReportingConfiguration)
@login_required
@require_permissions(['Run Group Reports'])
def peak_report(config):
    # modify config to only use first group id
    config.entity_ids = [config.entity_ids[0]]
    data = get_peak_report_data(config, g)

    return json.dumps(data)

def get_peak_report_data(config, g):
    """
    Gets the data for the peak web and pdf reports
    :param config:
    :param g:
    :return:
    """
    final_data = []
    for group in config.entity_ids:
        descendants = g.uow.groups.get_descendants(group)
        group_name = g.uow.groups.get_group_by_id(group).name
        accounts = []
        for gr in descendants:
            acc = g.uow.accounts.get_by_group_id_and_account_type(gr['id'], 'electric')
            for a in acc:
                accounts.append(a['id'])
        accounts = list(set(accounts))
        if len(accounts) <= 0:
            data = []
        else:
            data = g.uow.energy_records.get_peak_records(map(lambda record: [record, config.report_year], accounts))

        account_group = defaultdict(list)
        for entry in data:
            account_group[entry['account_id']].append(entry)

        for account in account_group:
            account_model = g.uow.accounts.get_by_id(account)
            date_group = defaultdict(list)
            for entry in account_group[account]:
                date_group[entry['readingdateutc'].strftime("%m/%d/%Y")].append(entry)
            for date in date_group:
                date_charts = {'name': 'Account: ' + account_model.name + ' - ' + date,
                               'temp_data': [],
                               'demand_data': [],
                               'date': date,
                               'demand_table_data': [],
                               'entity': group_name,
                               'account_name': account_model.name}
                # get all records for this date
                date_stamp = strptime(date, "%m/%d/%Y")
                date_records = g.uow.energy_records.get_all_for_account_date(account, date_stamp.tm_year,
                                                                             date_stamp.tm_mon, date_stamp.tm_mday)
                for record in date_records:
                    base_ten_time = record['readingdateutc'].hour + (record['readingdateutc'].minute * 1.0 / 60)
                    date_charts['temp_data'].append([base_ten_time, record['weather']['temp']])
                    date_charts['demand_data'].append([base_ten_time, record['energy']['demand']])
                    date_charts['demand_table_data'].append(
                        ["{:.2f}".format(record['energy']['demand']), record['readingdateutc'].strftime("%m/%d/%Y %H:%M")])
                date_charts['temp_data'] = sorted(date_charts['temp_data'], key=itemgetter(0))
                date_charts['demand_data'] = sorted(date_charts['demand_data'], key=itemgetter(0))
                date_charts['demand_table_data'] = sorted(date_charts['demand_table_data'], key=itemgetter(0))
                final_data.append(date_charts)
    return final_data

def get_accounts_for_group(group_id, account_type, report_year, comparison_type, demand_type, g):
    accounts = []
    # if demand type is specified, it needs to be included
    if demand_type != 'all':
        # find accounts for all or only electric/gas
        if account_type != 'all':
            acc = g.uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
            for a in acc:
                accounts.append([a['id'], comparison_type,  demand_type])
        else:
            for account in g.uow.accounts.get_all_for_group(group_id):
                accounts.append([account['id'], comparison_type, demand_type])
    else:
        # no demand type, so only worry if account type is all or only electric/gas
        if account_type != 'all':
            acc = g.uow.accounts.get_by_group_id_and_account_type(group_id, account_type)
            for a in acc:
                accounts.append([a['id'], comparison_type])
        else:
            for account in g.uow.accounts.get_all_for_group(group_id):
                accounts.append([account['id'], comparison_type])
    return accounts

@ReportingGroupsBlueprint.route("/api/ReportingGroups/GetEnergySummaryData", methods=["POST"])
@from_request_body("config", ReportingConfiguration)
@login_required
@require_any_permission(['Run Group Reports', 'View Dashboard'])
def get_energy_summary_data(config):

    total_energy_chart_info = TotalEnergyDataContainer()
    accounts_data=[]
    total_utility = 0
    total_reported = 0
    total_benchmark = 0
    total_cost_reduction = 0
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    # determine the x units
    x_units = "F"
    total_energy_chart_info.x_axis_label = "Temperature (" + x_units + ")"
    if config.comparison_type == "dewpt":
        x_units = "Dewpt"
        total_energy_chart_info.x_axis_label = "Dewpt"
    elif config.comparison_type == "enthalpy":
        x_units = "Enthalpy"
        total_energy_chart_info.x_axis_label = "Enthalpy"

    # get actual y units to send back, and get their equivalent column in the database
    # then call the proper report function determined by config.report_type

    if config.account_type == "electric":
        y_units = config.electric_units
        y_unit_map = 'sum_btu'
    elif config.account_type == "gas":
        y_units = config.gas_units
        y_unit_map = 'sum_btu'
    else:
        y_units = config.btu_units
        y_unit_map = "sum_btu"

    year_group_grouping = {}
    # loop through every group id in the configuration and get their consumption chart data
    for group_id in config.entity_ids:
        # get the group and descendants
        group = g.uow.groups.get_group_by_id(group_id)
        descendants = g.uow.groups.get_descendants(group_id)

        accounts = []
                # get all of the accounts for the given group id's descendants
        for gr in descendants:
            accounts += SharedReporting.get_accounts_for_group(gr['id'], config.account_type, config.report_year, config.comparison_type,
                                                       config.demand_type, g)
        # Get data associated with each account
        data = SharedReporting.get_total_energy_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type, y_units, y_unit_map, g)

        for year in data['year_data']:
            # check if the year has been added to the grouping before
            if not year in year_group_grouping:
            # the year hasn't been added to the grouping, so just create a new entry in dictionary
                year_group_grouping[year] = [{'entity': group.name,'data': data['year_data'][year]}]
            else:
                # the year has been added to the grouping before, so we append the new entry
                year_group_grouping[year].append({'entity': group.name,'data': data['year_data'][year]})

                 # loop through each group in each year and append to table data
    for entry in year_group_grouping[config.report_year]:
        accounts_data.append({'entity': entry['entity'],
            'utility': "{:,d}".format(int(round(entry['data']['utility']))),
            'reported': "{:,d}".format(int(round(entry['data']['reported']))),
            'benchmark': "{:,d}".format(int(round(entry['data']['benchmark']))),
            'difference': "{:,d}".format(int(round(entry['data']['difference']))),
            'change': "{:,.2f}%".format(float(entry['data']['change'])),
            'savings': locale.currency(int(round(entry['data']['cost_reduction'])),grouping=True)
            })
        # increase total energy for all years
        total_utility += entry['data']['utility']
        total_reported += entry['data']['reported']
        total_benchmark += entry['data']['benchmark']
        total_cost_reduction += entry['data']['cost_reduction']

    # calculate difference and change for all years
    total_difference = total_benchmark - total_reported
    if total_benchmark != 0:
        total_change = total_difference * 1.0 / total_benchmark * 100
    else:
        total_change = 0

    # add grand totals to the table data
    accounts_data.append({'entity': 'Grand Total',
                'utility': "{:,d}".format(int(round(total_utility))),
                'reported': "{:,d}".format(int(round(total_reported))),
                'benchmark': "{:,d}".format(int(round(total_benchmark))),
                'difference': "{:,d}".format(int(round(total_difference))),
                'change': "{:,.2f}%".format(total_change),
                'savings': locale.currency(int(round(total_cost_reduction)),grouping=True)
                })

    return json.dumps({"group_data":accounts_data})
