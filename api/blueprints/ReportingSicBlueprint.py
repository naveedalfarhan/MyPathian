from collections import defaultdict
import json
import locale
import math
from operator import itemgetter
from time import strptime
from api.models.ReportChartInformation import ReportChartInformation
from api.models.ReportingConfiguration import ReportingConfiguration
from api.models.TotalEnergyData import TotalEnergyData
from api.models.TotalEnergyDataContainer import TotalEnergyDataContainer
from extensions.binding import from_request_body, from_query_string, require_permissions, require_any_permission
from flask import Blueprint, g, abort, session, send_file
from flask.ext.login import login_required
from pdfgenerator.DataReports import DataReports
from reporting import SharedReporting

ReportingSicBlueprint = Blueprint("ReportingSicBlueprint", __name__)


@ReportingSicBlueprint.route("/api/ReportingSic/GetIntensityData", methods=["POST"])
@login_required
@from_request_body("config", ReportingConfiguration)
@require_permissions(['Run SIC Reports'])
def get_intensity_report(config):

    intensity_chart_info = get_intensity_chart_data(config.entity_ids, config.account_type, config.report_year,
                                                    config.comparison_type, config.demand_type, g)

    return json.dumps(intensity_chart_info.__dict__)


def get_intensity_chart_data(sic_codes, account_type, report_year, comparison_type, demand_type, g):
    # Set the x units for the intensity chart on the consumption report
    x_units = "F"
    x_axis_label = "Temperature (" + x_units + ")"
    if comparison_type == "enthalpy":
        x_axis_label = "Enthalpy"

    final_data = []

    # get all accounts for sic code and it's descendants
    for nc in sic_codes:
        data_insert = []
        accounts = []
        sic_code = g.uow.sic.get_by_code(nc)
        group_descendants = g.uow.sic.get_group_descendants(nc)
        for desc in group_descendants:
            accounts += SharedReporting.get_accounts_for_group(desc, account_type, report_year, comparison_type, demand_type, g)

        consider_demand_type = False
        if demand_type != 'all':
            consider_demand_type = True

        if len(accounts) > 0:
            # get data for the consumption report
            intensity_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(accounts, consider_demand_type=consider_demand_type)
        else:
            intensity_data = []

        # loop through and adjust the values based on size normalization
        for entry in intensity_data:
            data_insert.append([entry['group']['value'],
                                entry['reduction']['sum_btu'] / entry['reduction']['sum_size_normalization']])

        # add to the final data
        final_data.append({"name": sic_code["name"], "data": data_insert})

    # set the metadata for the consumption report
    intensity_chart_info = ReportChartInformation()
    intensity_chart_info.title = "Intensity"
    intensity_chart_info.y_axis_label = "Energy Intensity (BTU/sqft)"
    intensity_chart_info.x_axis_label = x_axis_label
    intensity_chart_info.data = final_data
    return intensity_chart_info


def get_total_energy_chart_data_web(sic_code, report_year, benchmark_year, account_type, comparison_type, demand_type,
                                    y_units, y_unit_map, g):
    """
    Gets the data for the energy consumption chart
    :param sic_code: sic code being reported on
    :param report_year: report year from configuration
    :param benchmark_year: benchmark year from configuration
    :param account_type: 'electric'/'gas'/'all'
    :param comparison_type: 'temp'/'dewpt'/'enthalpy'
    :param demand_type: 'all'/'peak'/'offpeak'
    :param y_units: y units used for reporting 'btu, mcf, etc'
    :param y_unit_map: mapping column for database (often 'sum_btu')
    :param g: g
    :return: object containing all necessary information
    """

    # determine if demand will be included in query
    consider_demand_type = False
    if demand_type != 'all':
        consider_demand_type = True

    same_year = report_year == benchmark_year

    # get unit factor for the selected y units
    unit_factor = SharedReporting.get_factor(y_units, y_unit_map)
    data = TotalEnergyData()

    # get group descendants of sic code
    descendants = g.uow.sic.get_group_descendants(sic_code)
    accounts = []

    # get all accounts for each group for the desired year
    for gr in descendants:
        accounts += SharedReporting.get_accounts_for_group(gr, account_type, report_year, comparison_type, demand_type, g)
        if not same_year:
            accounts += SharedReporting.get_accounts_for_group(gr, account_type, benchmark_year, comparison_type, demand_type, g)

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


def calculate_pf_data(account_group, report_year, benchmark_year, same_year):
    """
    Calculates the powerfactor data for the account
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

    kwh_unit_factor = SharedReporting.get_factor('kwh', 'sum_btu')

    # if the benchmark year and current year are the same they will be handled differently
    if same_year:
        for value in grouped_keys:
            entry = account_group[value][0]

            # calculate powerfactor
            record_kwh = entry["reduction"]["sum_btu"] * kwh_unit_factor
            record_kvar = math.sqrt(math.pow(record_kwh, 2) + math.pow(entry['reduction']['sum_kvar'], 2))
            record_pf = record_kwh * 1.0 / record_kvar

            # update lists of data
            reported_consumption.append([value, round(record_pf, 5)])
            diff.append([value, 0])
            benchmark_consumption.append([value, round(record_pf, 5)])
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
                        # calculate powerfactor
                        record_kwh = record['reduction']['sum_btu'] * kwh_unit_factor
                        record_kvar = math.sqrt(math.pow(record_kwh, 2) + math.pow(record['reduction']['sum_kvar'], 2))
                        record_pf = record_kwh * 1.0 / record_kvar

                        report_record_hours = record['reduction']['sum_hours_in_record']
                        reported_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / report_record_hours

                        # update list
                        reported_consumption.append([value, round(record_pf, 5)])
                    elif record['group']['year'] == benchmark_year:
                        benchmark_avg_size = record['reduction']['sum_size_normalization'] * 1.0 / record['reduction']['sum_hours_in_record']
                        benchmark_record_btu_normalized = record['reduction']['sum_btu']
                        benchmark_record_kvar_normalized = record['reduction']['sum_kvar']

                # normalize the btu and kvar to properly calculate pf
                size_ratio = reported_avg_size * 1.0 / benchmark_avg_size
                benchmark_record_btu_normalized *= size_ratio
                benchmark_record_kvar_normalized *= size_ratio
                benchmark_kwh = benchmark_record_btu_normalized * kwh_unit_factor
                benchmark_kvar = math.sqrt(math.pow(benchmark_kwh, 2) + math.pow(benchmark_record_kvar_normalized, 2))
                benchmark_pf = benchmark_kwh * 1.0 / benchmark_kvar

                # update lists
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


def get_pf_chart_data_web(sic_code, report_year, benchmark_year, comparison_type, demand_type, g):
    """
    Gets and calculates all data needed for powerfactor charts
    :param sic_code: sic code to find data for
    :param report_year: report year
    :param benchmark_year: benchmark year
    :param comparison_type: 'temp'/'dewpt'/'enthalpy'
    :param demand_type: 'all'/'peak'/'offpeak'
    :param g:
    :return: data for the charts
    """

    data_list = []

    sic_obj = g.uow.sic.get_by_code(sic_code)
    descendants = g.uow.sic.get_group_descendants(sic_code)
    accounts = []

    # get all accounts of group descendants of sic code
    for gr in descendants:
        accounts += SharedReporting.get_accounts_for_group(gr, 'Electric', report_year, comparison_type, demand_type, g)
        accounts += SharedReporting.get_accounts_for_group(gr, 'Electric', benchmark_year, comparison_type, demand_type, g)

    # get the benchmark data for the accounts to avoid looping through benchmark data multiple times
    report_data = g.uow.compiled_energy_records.get_compiled_energy_records_for_report(accounts, data_field_name='sum_kvar')

    # create a copy of the benchmark records
    account_group = defaultdict(list)
    for d in report_data:
        account_group[d['group']['value']].append(d)

    calculated_totals = calculate_pf_data(account_group, report_year, benchmark_year, report_year == benchmark_year)

    return calculated_totals

@ReportingSicBlueprint.route("/api/ReportingSic/GetTotalEnergyData", methods=["POST"])
@login_required
@from_request_body("config", ReportingConfiguration)
@require_permissions(['Run SIC Reports'])
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
    else:
        abort(409)

    # make sure data exists, otherwise return an empty object
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
    if config.report_type == 'powerfactor':
        data = get_pf_chart_data_web(config.entity_ids[0], config.report_year, config.benchmark_year, config.comparison_type, config.demand_type, g)
    else:
        # we only care about the first entity id since the configuration is being formatted before the request as [entity_id]
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


@ReportingSicBlueprint.route("/api/ReportingSic/GetGroups", methods=["GET"])
@login_required
@from_query_string("code", str, "code")
@require_any_permission(['Manage Groups', 'View Groups'])
def get_groups(code):
    groups = g.uow.sic.get_group_descendants(code)
    group_list = g.uow.groups.get_all(groups)
    group_list = sorted(group_list, key=lambda k: k['name'])
    return json.dumps(group_list)


def get_peak_report_data(config, g):
    """
    Gets the data for the peak web and pdf reports
    :param config: configuration of the report
    :param g: g
    :return: object containing peak data
    """

    final_data = []
    for sic_code in config.entity_ids:
        descendants = g.uow.sic.get_group_descendants(sic_code)
        sic_name = g.uow.sic.get_by_code(sic_code)["name"]
        accounts = []
        # get all accounts for sic code descendants
        for group in descendants:
            acc = g.uow.accounts.get_by_group_id_and_account_type(group, 'Electric')
            for a in acc:
                accounts.append(a['id'])

        # make list of accounts distinct
        accounts = list(set(accounts))

        # get energy data from non-compiled energy records
        if len(accounts) < 1:
            data = []
        else:
            # format data in the proper way for the peak records function
            data = g.uow.energy_records.get_peak_records(map(lambda record: [record, config.report_year], accounts))

        # group the data by accounts
        account_group = defaultdict(list)
        for entry in data:
            account_group[entry['account_id']].append(entry)

        # loop through each account and get data
        for account in account_group:
            account_model = g.uow.accounts.get_by_id(account)
            # group account records by date
            date_group = defaultdict(list)
            for entry in account_group[account]:
                # convert the date to a string and then append to it's entry
                date_group[entry['readingdateutc'].strftime("%m/%d/%Y")].append(entry)

            for date in date_group:
                date_charts = {'name': 'Account: ' + account_model.name + ' - ' + date,
                               'temp_data': [],
                               'demand_data': [],
                               'date': date,
                               'demand_table_data': [],
                               'entity': sic_name,
                               'account_name': account_model.name}
                # get all records for this date
                date_stamp = strptime(date, "%m/%d/%Y")
                date_records = g.uow.energy_records.get_all_for_account_date(account, date_stamp.tm_year,
                                                                             date_stamp.tm_mon, date_stamp.tm_mday)

                for record in date_records:
                    # get the base ten time for the charts (hour, 0-24)
                    base_ten_time = record['readingdateutc'].hour + (record['readingdateutc'].minute * 1.0 / 60)
                    date_charts['temp_data'].append([base_ten_time, record['weather']['temp']])
                    date_charts['demand_data'].append([base_ten_time, record['energy']['demand']])
                    date_charts['demand_table_data'].append(
                        ["{:.2f}".format(record['energy']['demand']), record['readingdateutc'].strftime("%m/%d/%Y %H:%M")])

                # sort the data by base ten time
                date_charts['temp_data'] = sorted(date_charts['temp_data'], key=itemgetter(0))
                date_charts['demand_data'] = sorted(date_charts['demand_data'], key=itemgetter(0))
                date_charts['demand_table_data'] = sorted(date_charts['demand_table_data'], key=itemgetter(0))
                final_data.append(date_charts)
    return final_data

@ReportingSicBlueprint.route('/api/ReportingSic/peak', methods=["POST"])
@from_request_body("config", ReportingConfiguration)
@login_required
@require_permissions(['Run SIC Reports'])
def peak_report(config):
    return json.dumps(get_peak_report_data(config, g))


def generate_consumption_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g):
    """
    Gathers data and generates a pdf from it
    :param config:
    :param y_units:
    :param y_unit_map:
    :param total_energy_chart_info:
    :param submitted_by_user:
    :param submitted_to:
    :param g:
    :return:
    """
    # collect information for intensity chart
    intensity_chart_info = get_intensity_chart_data(config.entity_ids, config.account_type, config.report_year,
                                                    config.comparison_type, config.demand_type, g)

    year_group_grouping = {}
    # loop through every SIC code in the configuration and get their consumption chart data
    for code in config.entity_ids:
        # get the sic code and it's group descendants
        sic_code = g.uow.sic.get_by_code(code)
        group_descendants = g.uow.sic.get_group_descendants(code)

        # get all accounts for the SIC code
        accounts = []
        for gr in group_descendants:
            accounts += SharedReporting.get_accounts_for_group(gr, config.account_type, config.report_year,
                                                               config.comparison_type, config.demand_type, g)

        # get data associated with each account
        data = SharedReporting.get_total_energy_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type,
                                               y_units, y_unit_map, g)
        total_energy_chart_info.data.append({'entity': sic_code['name'], 'data': data['chart_data']})

        for year in data['year_data']:
            # check if the year has not been added to the group before
            if not year in year_group_grouping:
                # the year hasn't been added to the grouping, so just create a new entry in the dictionary
                year_group_grouping[year] = [{'entity': sic_code['name'] + ' (' + str(year) + ')',
                                              'data': data['year_data'][year]}]
            else:
                # append the entry
                year_group_grouping[year].append({'entity': sic_code['name'] + ' (' + str(year) + ')',
                                                  'data': data['year_data'][year]})

    # generate report data and get the report path
    report_path = DataReports.generate_consumption_report(config.report_year, config.benchmark_year,
                                                          intensity_chart_info, total_energy_chart_info,
                                                          year_group_grouping, submitted_by_user, submitted_to,
                                                          SharedReporting.get_y_unit_label(y_units))
    return report_path

def generate_powerfactor_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g):
    """
    Gathers data for powerfactor report and generates it's PDF
    :param config: report config
    :param y_units: y units
    :param y_unit_map: database column name for y units
    :param total_energy_chart_info: TotalEnergyChartInfo object to hold data
    :param submitted_by_user: user who submitted the report
    :param submitted_to: group who the report is addressed to
    :param g: g
    :return: path to the PDF
    """
    for code in config.entity_ids:
        sic_code = g.uow.sic.get_by_code(code)

        # get all accounts for sic code
        group_descendants = g.uow.sic.get_group_descendants(code)
        accounts = []
        # Get all accounts for each group for the desired year
        for gr in group_descendants:
            accounts += SharedReporting.get_accounts_for_group(gr, 'Electric', config.report_year, config.comparison_type, config.demand_type, g)

        # Get data associated with each account
        data = SharedReporting.get_pf_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type, g)
        total_energy_chart_info.data.append({'entity': sic_code["name"], 'data': data})

    # Generate consumption report with data
    report_path = DataReports.generate_powerfactor_report(config.report_year, config.benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to)
    return report_path


def generate_kvah_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g):
    """
    Gathers data for the kVa report and generates it's PDF
    :param config: report configuration
    :param y_units: y units for report
    :param y_unit_map: database column name for y units
    :param total_energy_chart_info: TotalEnergyChartInfo object
    :param submitted_by_user: user who submitted the report
    :param submitted_to: group that the report is addressed to
    :param g: g
    :return: path to report
    """
    for code in config.entity_ids:
        sic_code = g.uow.sic.get_by_code(code)

        # get all accounts for sic code
        group_descendants = g.uow.sic.get_group_descendants(code)
        accounts = []
        for gr in group_descendants:
            accounts += SharedReporting.get_accounts_for_group(gr, 'Electric', config.report_year, config.comparison_type, config.demand_type, g)

        # Get data associated with each account
        data = SharedReporting.get_total_energy_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type, y_units, y_unit_map, g)
        total_energy_chart_info.data.append({'entity': sic_code["name"], 'data': data})

    # Generate consumption report with data
    report_path = DataReports.generate_kvah_report(config.report_year, config.benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to)
    return report_path
    

def generate_kvarh_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g):
    """
    Gathers data for the kVar report and generates it's PDF
    :param config: report configuration
    :param y_units: y units
    :param y_unit_map: database column name for y unit
    :param total_energy_chart_info: TotalEnergyChartInfo object to hold data
    :param submitted_by_user: user who submitted the report
    :param submitted_to: group who the report what submitted to
    :param g: g
    :return: path to the report PDF
    """
    for code in config.entity_ids:
        sic_code = g.uow.sic.get_by_code(code)

        # get data associated with each account in the sic code
        accounts = []
        group_descendants = g.uow.sic.get_group_descendants(code)
        for gr in group_descendants:
            accounts += SharedReporting.get_accounts_for_group(gr, 'Electric', config.report_year, config.comparison_type, config.demand_type, g)
        data = SharedReporting.get_total_energy_chart_data_pdf(accounts, config.report_year, config.benchmark_year, config.demand_type, y_units, y_unit_map, g)
        total_energy_chart_info.data.append({'entity': sic_code["name"], 'data': data})

    # Generate consumption report with data
    report_path = DataReports.generate_kvarh_report(config.report_year, config.benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to)
    return report_path
    

def generate_consumptiontext_report(config, submitted_by_user, g):
    """
    Gathers data for consumption text report and generates it's PDF
    :param config: report configuration
    :param submitted_by_user: user who submitted the report
    :param g: g
    :return: report path
    """
    report_path = DataReports.generate_consumptiontext_report(config.report_year, config.benchmark_year, SharedReporting.generate_consumptiontext_report(config, 'sic', g), submitted_by_user, config.account_type)
    return report_path


def generate_peak_report(config, submitted_by_user, submitted_to, g):
    """
    Gathers data for peak report and generates it's PDF
    :param config: report configuration
    :param submitted_by_user: user who submitted the report
    :param submitted_to: group the report is addressed to
    :param g: g
    :return: path to PDF report
    """
    data = get_peak_report_data(config, g)

    # generate peak report with data
    report_path = DataReports.generate_peak_report(data, config.report_year, submitted_by_user, submitted_to)
    return report_path


def generate_variance_report(config, y_units, y_unit_map, submitted_by_user, submitted_to, g):
    """
    Gathers data for variance report and generates it's PDF
    :param config: report configuration
    :param y_units: y units
    :param y_unit_map: database column name for y units
    :param submitted_by_user: user who submitted the report
    :param submitted_to: group who the report is addressed to
    :param g: g
    :return: path to PDF of report
    """
    total_data = []
    for code in config.entity_ids:
        sic_code = g.uow.sic.get_by_code(code)

        # get all accounts for sic code
        group_descendants = g.uow.sic.get_group_descendants(code)
        accounts = []

        # check to make sure we should get electric accounts
        if config.account_type.lower() != 'gas':
            # get all electric accounts
            for desc in group_descendants:
                accounts += SharedReporting.get_accounts_for_group(desc, 'Electric', config.report_year, config.comparison_type, config.demand_type, g)
                accounts += SharedReporting.get_accounts_for_group(desc, 'Electric', config.benchmark_year, config.comparison_type, config.demand_type, g)

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
            for desc in group_descendants:
                accounts += SharedReporting.get_accounts_for_group(desc, 'Gas', config.report_year, config.comparison_type, config.demand_type, g)
                accounts += SharedReporting.get_accounts_for_group(desc, 'Gas', config.benchmark_year, config.comparison_type, config.demand_type, g)

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

        data = {"entity_name": sic_code["name"], "sitedata": [
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
        data["entity_name"] = sic_code["name"]
        data["sitedata"][0]["data"] = utility_list
        data["sitedata"][1]["data"] = actual_list
        data["sitedata"][2]["data"] = benchmark_list
        data["sitedata"][3]["data"] = plan_list
        data["sitedata"][4]["data"] = cost_variance_list
        data["sitedata"][5]["data"] = percent_variance_list
        total_data.append(data)
    report_path = DataReports.generate_variance_report(total_data, config.report_year, config.benchmark_year, submitted_by_user, submitted_to)
    return report_path


@ReportingSicBlueprint.route("/api/ReportingSic/GetReport", methods=["POST"])
@login_required
@from_request_body("config", ReportingConfiguration)
def get_report(config):
    report_name = "DefaultReportName"
    report_path = ""

    # make sure submitted_to isn't empty
    if not config.submitted_to:
        abort(400)

    submitted_by_user = g.uow.users.get_user_by_id(session["current_user"]["id"])
    submitted_to = config.submitted_to

    # get submitted_by and submitted_to
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
        if config.account_type.lower() == "electric":
            y_units = config.electric_units
            y_unit_map = 'sum_btu'
            total_energy_chart_info.title = 'Total Energy Usage - Electric'
        elif config.account_type.lower() == 'gas':
            y_units = config.gas_units
            y_unit_map = 'sum_btu'
            total_energy_chart_info.title = 'Total Energy Usage - Gas'
        else:
            y_units = config.btu_units
            y_unit_map = "sum_btu"
            total_energy_chart_info.title = 'Total Energy Usage'
        total_energy_chart_info.y_axis_label = 'Average Energy Usage (' + SharedReporting.get_y_unit_label(y_units) + ')'

        # generate consumption report
        report_path = generate_consumption_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g)
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
    elif config.report_type == "kvar":
        report_name = "kVArh"
        y_units = "kvar"
        y_unit_map = "sum_kvar"
        total_energy_chart_info.y_axis_label = "Average Electric Usage (kVar)"
        total_energy_chart_info.title = "kVar"
        report_path = generate_kvarh_report(config, y_units, y_unit_map, total_energy_chart_info, submitted_by_user, submitted_to, g)
    elif config.report_type == "text":
        report_name = "Consumption Text Report"
        report_path = generate_consumptiontext_report(config, submitted_by_user, g)
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

    return send_file(report_path, mimetype='application/pdf', as_attachment=True, attachment_filename=report_name + '.pdf')