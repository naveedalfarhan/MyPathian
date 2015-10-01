from collections import defaultdict
import json

from api.models.ReportChartInformation import ReportChartInformation
from api.models.TotalEnergyDataContainer import TotalEnergyDataContainer
from api.models.component_difference_data_container import ComponentDifferenceDataContainer
from api.models.component_reporting_comparison_configuration import ComponentReportingComparisonConfiguration
from api.models.component_reporting_difference_configuration import ComponentReportingDifferenceConfiguration
from api.models.equipment_report import EquipmentReport

from flask import Blueprint, g, abort, session, send_file
from api.models.component_reporting_configuration import ComponentReportingConfiguration
from extensions.binding import from_request_body, from_query_string
from flask.ext.login import login_required
from pdfgenerator.DataReports import DataReports
from reporting import SharedReporting


ReportingComponentsBlueprint = Blueprint("ReportingComponentsBlueprint", __name__)


@ReportingComponentsBlueprint.route("/api/ReportingComponents/PointSelectionTree", methods=["GET"])
@from_query_string("component_id", str, prop_name="id")
@login_required
def point_selection_tree(component_id):
    if component_id is None or component_id[0:11] == "components:":
        if component_id is not None:
            component_id = component_id[11:]
        components = g.uow.components.get_structure_children_of(component_id)
        for c in components:
            c["id"] = "component:" + c["id"]
            c["name"] = c["num"] + " " + c["description"]
            c["hasChildren"] = True
        return json.dumps(components)
    elif component_id[0:7] == "points:":
        component_id = component_id[7:]

        points = g.uow.component_points.get_points_for_component_id(component_id)

        # only use points where the point is calculated or energy
        points = [p for p in points if 'point_type' in p and p['point_type'] == 'EP' or p['point_type'] == 'CP']

        points = [{"id": "point:" + p["id"], "name": p["component_point_num"], "hasChildren": False}
                  for p in points]
        return json.dumps(points)
    elif component_id[0:10] == "component:":
        component_id = component_id[10:]
        components = [
            {"id": "components:" + component_id, "name": "Components", "hasChildren": True},
            {"id": "points:" + component_id, "name": "Points", "hasChildren": True}
        ]
        return json.dumps(components)


@ReportingComponentsBlueprint.route("/api/ReportingComponents/ReportingTree", methods=["GET"])
@from_query_string("component_id", str, prop_name="id")
@login_required
def reporting_component_tree(component_id):
    if component_id is None:
        # root of tree = groups
        groups = g.uow.groups.get_child_groups_of(component_id)
        for gr in groups:
            gr["id"] = "group:" + gr["id"]
            gr["hasChildren"] = True
        return json.dumps(groups)
    elif component_id[0:6] == "group:":
        # group, so get the groups and equipment underneath it
        component_id = component_id[6:]
        groups = g.uow.groups.get_child_groups_of(component_id)
        for gr in groups:
            gr["id"] = "group:" + gr["id"]
            gr["hasChildren"] = True
        equipment = g.uow.equipment.get_equipment_for_group(component_id)
        for e in equipment:
            e["id"] = "equip:" + e["id"]
            e["hasChildren"] = True

        combined = groups + equipment
        combined = sorted(combined, key=lambda k: k['name'])
        return json.dumps(combined)
    elif component_id[0:6] == "equip:":
        # equipment, so get the equipment points underneath it
        component_id = component_id[6:]
        equipment_points = g.uow.equipment.get_equipment_reporting_points(component_id)
        for e in equipment_points:
            e["id"] = "point:" + e["id"]
            e["hasChildren"] = False
            e["name"] = e['point_code']

        equipment_points = sorted(equipment_points, key=lambda k: k['name'])
        return json.dumps(equipment_points)


@ReportingComponentsBlueprint.route("/api/ReportingComponents/StandardsChart", methods=["POST"])
@from_request_body("config", ComponentReportingConfiguration)
def get_standards_chart(config):
    standards_chart_info = get_standards_chart_data(config)
    return json.dumps(standards_chart_info.__dict__)


def get_standards_chart_data(config):
    data = g.uow.compiled_point_records.get_compiled_point_data(config.point_ids, config.report_year,
                                                                'temp', 'all')

    standards_chart_info = ReportChartInformation()
    standards_chart_info.title = "Intensity"
    standards_chart_info.y_axis_label = "Energy Intensity (BTU/sqft)"
    standards_chart_info.x_axis_label = "Temperature (F)"
    standards_chart_info.data = data
    return standards_chart_info


def generate_standards_pdf(config, standards_chart_info, standards_table_info, submitted_by, submitted_to):
    """
    Generates an standards PDF and returns the path to the file
    :param config: report configuration
    :param standards_chart_info: standards chart info
    :param standards_table_info: standards table information
    :param submitted_by: user submitting the report
    :param submitted_to: group the report is for
    :return: path to pdf
    """
    return DataReports.generate_component_standards_report(config, standards_chart_info, standards_table_info,
                                                           submitted_by, submitted_to)


@ReportingComponentsBlueprint.route("/api/ReportingComponents/GetStandardsPDFReport", methods=["POST"])
@from_request_body("config", ComponentReportingConfiguration)
def get_standards_pdf_report(config):
    if not config.submitted_to:
        return abort(409)

    submitted_by = g.uow.users.get_user_by_id(session["current_user"]["id"])
    submitted_to = config.submitted_to

    # get the submitted by and submitted to
    submitted_by, submitted_to = SharedReporting.get_submitted_contacts(submitted_by, submitted_to, g)

    total_energy_chart_info = TotalEnergyDataContainer()

    report_name = "Component Standards Report"
    total_energy_chart_info.y_axis_label = "Energy Consumption (BTU/sqft)"
    total_energy_chart_info.title = "Intensity"
    standards_data = get_standards_chart_data(config)
    standards_table_data = get_standards_table_data(config)
    report_path = generate_standards_pdf(config, standards_data, standards_table_data, submitted_by, submitted_to)

    # send file back out to user for download
    return send_file(report_path, mimetype='application/pdf', as_attachment=True, attachment_filename=report_name + '.pdf')


def get_standards_table_data(config):
    """
    Calculates and formats all data for the component standards report table
    :param config:
    :return:
    """
    final_data_dict = {}
    lowest_ppsn_point = None
    lowest_ppsn = 99999999
    for point_id in config.point_ids:
        point = g.uow.component_points.get_by_component_point_num(point_id)

        # get the syrx nums for the component point in order to get the ppsn
        syrx_nums = g.uow.component_points.get_syrx_nums_for_component_point(point_id)

        if len(syrx_nums) > 0:
            # get the ppsn for the syrx numbers
            ppsn = g.uow.compiled_point_records.get_ppsn(syrx_nums, config.report_year)['ppsn']

            if ppsn < lowest_ppsn and ppsn != 0:
                lowest_ppsn = ppsn
                lowest_ppsn_point = point_id
        else:
            # no syrx numbers so ppsn is 0, and it doesn't count towards bic
            ppsn = 0

        # make sure the point exists and get it, as it will be in a list
        if len(point) > 0:
            point = point[0]

        final_data_dict[point_id] = {'component': point_id, 'description': point['description'], 'units': point['units'],
                                     'ppsn': ppsn, 'bic': '', 'diff': "0.00%"}

    if lowest_ppsn_point:
        # find the record of the bic ppsn
        final_data_dict[lowest_ppsn_point]['bic'] = 'X'

        # loop through each record and update diff
        if lowest_ppsn != 0:
            for key in final_data_dict:
                if key == lowest_ppsn_point:
                    continue
                row_ppsn = final_data_dict[key]['ppsn']
                final_data_dict[key]['diff'] = "{:.2f}%".format(((lowest_ppsn - row_ppsn) * 1.0 / lowest_ppsn) * 100.0)

    final_data = final_data_dict.values()
    final_data = sorted(final_data, key=lambda x: x['component'])

    return final_data


@ReportingComponentsBlueprint.route("/api/ReportingComponents/StandardsTable", methods=["POST"])
@from_request_body("config", ComponentReportingConfiguration)
@login_required
def get_standards_table(config):
    standards_table_data = get_standards_table_data(config)
    return json.dumps(standards_table_data)


@ReportingComponentsBlueprint.route("/api/ReportingComponents/ComparisonChart", methods=["POST"])
@from_request_body("config", ComponentReportingComparisonConfiguration)
@login_required
def get_comparison_chart(config):
    final_return = get_comparison_chart_data(config)
    return json.dumps(final_return.__dict__)


@ReportingComponentsBlueprint.route("/api/ReportingComponents/ComparisonTable", methods=["POST"])
@from_request_body("config", ComponentReportingComparisonConfiguration)
@login_required
def get_comparison_table(config):
    rows = get_comparison_table_data(config, config.comparison_year)
    return json.dumps({"rows": rows})


def get_syrx_nums_for_groups(groups):
    """
    Returns a list of all master syrx nums for a given list of groups
    :param groups: list of group objects
    :return: list of numbers
    """
    point_nums = []
    for group in groups:
        equips = g.uow.equipment.get_equipment_for_group(group["id"])
        for equip in equips:
            points = g.uow.equipment.get_master_equipment_points(equip["id"])
            point_nums += map(lambda x: x['equipment_point_id'], points)
    return point_nums


def get_syrx_nums_from_entity(entity):
    """
    Gets a list of component ids based on the given type of entity
    :param entity: id prefixed by 'point'/'equip'/'group'
    :return: list of component ids
    """
    if entity[0:6] == "group:":
        group_id = entity[6:]
        groups = g.uow.groups.get_child_groups_of(group_id)
        # add current group to the list
        groups += [{'id': group_id}]
        syrx_nums = get_syrx_nums_for_groups(groups)
    elif entity[0:6] == "equip:":
        equipment_id = entity[6:]
        syrx_nums = g.uow.equipment.get_equipment_reporting_points(equipment_id)
        syrx_nums = map(lambda x: x['id'], syrx_nums)
    else:
        # equipment point
        syrx_nums = [entity[6:]]
    return syrx_nums


def get_label_for_entity(entity):
    """
    Gets a string label for the reporting entity
    :param entity: 'group'/'equip'/'point'
    :return: string
    """
    if entity[0:6] == "group:":
        group_id = entity[6:]
        group = g.uow.groups.get_group_raw_by_id(group_id)
        label = group["name"]
    elif entity[0:6] == "equip:":
        equipment_id = entity[6:]
        equipment = g.uow.equipment.get_by_id(equipment_id)
        label = equipment.name
    else:
        # equipment point
        syrx_num = entity[6:]
        ep = g.uow.equipment.get_equipment_point_by_syrx_num(syrx_num)
        label = ep['point_code']
    return label


def convert_data_to_btu_unit(data, conversion_factor):
    """
    Converts the data to the proper btu unit based on conversion_factor
    :param data: [[x, y-value], [x, y-value], ...]
    :param conversion_factor: conversion factor to turn y-value into btu
    :return:
    """
    for d in data:
        d[1] *= conversion_factor


def add_to_new_series_data(new_series_data, data_to_add):
    """
    Adds data from data_to_add to the proper x-values in new_series data
    :param new_series_data: dict of [x-value, y-value}
    :param data_to_add: [[x, y], [x, y], ...]
    """
    for d in data_to_add:
        if d[0] in new_series_data:
            new_series_data[d[0]] += d[1]
        else:
            new_series_data[d[0]] = d[1]

def get_comparison_chart_data(config):
    """
    Gets a list of the series used for the comparison report charts
    :param config: ComponentReportingComparisonConfiguration
    :return: TotalEnergyDataContainer that holds all information for the chart
    """
    series_list = []
    for entity in config.component_ids:
        # get label from the entity
        label = get_label_for_entity(entity)

        # get actual component_id from the list
        syrx_nums = get_syrx_nums_from_entity(entity)

        # combine the comparison year with the historical mode years
        all_years = list(set([config.comparison_year] + config.historical_years))
        for year in all_years:
            new_series_data = {}
            for syrx_num in syrx_nums:
                # get the equipment point by syrx num
                ep = g.uow.equipment.get_equipment_point_by_syrx_num(syrx_num)

                # get the series data for each point
                syrx_series = g.uow.compiled_point_records.get_data_for_syrx_nums([syrx_num], year, 1, 12)

                if len(syrx_series) > 0:
                    # convert the data to the new values
                    conversion_factor = SharedReporting.get_component_point_conversion(ep['units'].lower(), config.unit)

                    convert_data_to_btu_unit(syrx_series[0]['data'], conversion_factor)

                    # add to the new_series_data
                    add_to_new_series_data(new_series_data, syrx_series[0]['data'])

            if len(new_series_data) > 0:
                new_series_data_list = []
                # change the data from a dictionary to list
                for key in sorted(new_series_data.keys()):
                    new_series_data_list.append([key, new_series_data[key]])

                # overwrite the point name with the component name
                new_series = [{"name": None,
                               "data": new_series_data_list}]
                new_series[0]["name"] = label + " - " + str(year)

                series_list += new_series

    chart_info = TotalEnergyDataContainer()
    chart_info.title = "Intensity"
    chart_info.data = series_list
    chart_info.x_axis_label = "Temperature (F)"
    chart_info.y_axis_label = "Energy Consumption (" + SharedReporting.get_y_unit_label(config.unit) + ")"

    return chart_info


def calculate_final_row_values(bic_syrx_num, bic_consumption, bic_hours, new_row, price):
    """
    Calculates the differences for the columns in the table
    :param bic_syrx_num: syrx_num of BIC component
    :param bic_consumption: consumption of BIC component
    :param bic_hours: hours_in_record of BIC component
    :param new_row: new row dictionary, in form {'component_id', 'consumption', 'hours', 'row':dict}
    :param price: price/unit
    :return:
    """
    conversion_factor = new_row['conversion_factor']

    if new_row['syrx_num'] == bic_syrx_num:
        # if the component is bic, give it a row class and a % diff of 0
        new_row['row']['class'] = 'bic'
        new_row['row']['diff'] = 0.0
        new_row['row']['hour_diff'] = 0
        new_row['row']['year_diff'] = 0
        new_row['row']['hour_cost_diff'] = 0
        new_row['row']['year_cost_diff'] = 0
    else:
        # calculate all the fields necessary for the table
        hours_per_year = 8760

        # prevent divide by 0
        if bic_hours == 0:
            bic_per_hour = 0
        else:
            bic_per_hour = (bic_consumption * 1.0) / bic_hours

        # prevent divide by 0
        if new_row['hours'] == 0:
            row_per_hour = 0
        else:
            row_per_hour = (new_row['consumption'] * 1.0) / new_row['hours']

        # find the raw consumption difference
        if bic_consumption == 0:
            new_row['row']['diff'] = 0.0
        else:
            new_row['row']['diff'] = "{:,}".format(round(((bic_consumption - new_row['consumption']) * 1.0 / bic_consumption) * 100.0,
                                                   2))

        # calculate the differences using the energy/hour and energy/year values
        new_row['row']['hour_diff'] = "{:,}".format(round(bic_per_hour - row_per_hour, 2))

        bic_per_year = bic_per_hour * hours_per_year
        row_per_year = row_per_hour * hours_per_year

        new_row['row']['year_diff'] = "{:,}".format(round(bic_per_year - row_per_year, 2))

        new_row['row']['hour_cost_diff'] = "{:,}".format(round(((bic_per_hour / conversion_factor) * price) - ((row_per_hour / conversion_factor) * price), 2))
        new_row['row']['year_cost_diff'] = "{:,}".format(round(((bic_per_year / conversion_factor) * price) - ((row_per_year / conversion_factor) * price), 2))

    return new_row['row']


def construct_row(syrx_num, component_values, unit):
    """
    Constructs a row for the table
    :param syrx_num: syrx_num that is being reported on
    :param component_values: dictionary containing ppsn, sum_value, and sum_hours_in_record
    :param unit: Unit the result should be in
    :return:
    """
    equipment_point = g.uow.equipment.get_equipment_point_by_syrx_num(syrx_num)
    equipment = g.uow.equipment.get_by_id(equipment_point['equipment_id'])
    component = g.uow.components.get_by_id(equipment_point['component_id'])
    row_dict = {
        'row': {
            'equipment_name':equipment.name, 'component_id': component.num,
            'description': equipment_point['point_code'],
            'units': SharedReporting.get_y_unit_label(unit)
        },
        'ppsn': component_values['ppsn'],
        'hours': component_values['sum_hours_in_record'],
        'consumption': component_values['sum_value'],
        'component_id': component.id,
        'syrx_num': syrx_num,
        'conversion_factor': None}
    return row_dict


def get_comparison_price(units, reporting_group_id):
    """
    Gets the price to use for comparing component efficieny
    :param units: unit to use
    :param reporting_group_id: group to find price from accounts for
    :return:
    """
    # get the proper account for the group, and use it's most up-to-date price normalization
    if units == 'kwh':
        # electric account
        accounts = g.uow.accounts.get_by_group_id_and_account_type(reporting_group_id, 'Electric')
        if len(accounts) < 1:
            price = 0
        else:
            # get the price normalization for the first account in the list, and extract the value from the model
            price = g.uow.price_normalizations.get_most_recent_for_account(accounts[0]['id'])
            price = price.value
    else:
        # gas
        accounts = g.uow.accounts.get_by_group_id_and_account_type(reporting_group_id, 'Gas')
        if len(accounts) < 1:
            price = 0
        else:
            # get the price normalization for the first account that has a price in the list, and extract the value from the mode
            price = 0
            for a in accounts:
                price = g.uow.price_normalizations.get_most_recent_for_account(a['id'])
                if price:
                    price = price.value
                    break
    return price


def get_all_component_master_point_mappings(component_ids):
    """
    Gets a dictionary of master points for each component in list
    :param component_ids: list of component id's to get master points for
    :return: {'component_id': list of master points}
    """
    return_dict = {}
    for component_id in component_ids:
        # get master point mappings for component
        mappings = g.uow.components.get_component_master_point_mappings(component_id)
        master_points = [m["master_point_num"] for m in mappings]

        return_dict[component_id] = master_points

    return return_dict


def get_comparison_table_data(config, year):
    """
    Gets the rows for the data table after the chart
    :param config: ComponentReportingComparisonConfiguration
    :param year: year for the report
    :return: list of rows
    """
    rows = []
    row_dict_list = []
    bic_syrx_num = None
    bic_value = None
    bic_hours = None
    bic_ppsn = None

    syrx_nums_used = set()

    # get price for reporting group
    price = get_comparison_price('btu', config.submitted_to)

    for entity in config.component_ids:
        # since the application allows for groups, equipment, and equipment points to be selected, we need to get
        # the syrx nums for whatever the current reporting entity is.

        # only get the syrx nums which haven't been used yet
        syrx_nums = get_syrx_nums_from_entity(entity)
        syrx_nums = list(set(syrx_nums) - syrx_nums_used)

        # update list of used syrx nums
        syrx_nums_used |= set(syrx_nums)

        for syrx_num in syrx_nums:
            # get PPSN for the entity
            component_values = g.uow.compiled_point_records.get_ppsn([syrx_num], year)

            # convert the values
            units = g.uow.equipment.get_equipment_point_by_syrx_num(syrx_num)['units']
            conversion_factor = SharedReporting.get_component_point_conversion(units, config.unit)

            component_values['sum_value'] *= conversion_factor
            component_values['ppsn'] *= conversion_factor

            # add a dictionary of row data to the row_dict
            row_dict = construct_row(syrx_num, component_values, config.unit)

            row_dict['conversion_factor'] = conversion_factor

            # set the bic value if it has not yet been set
            if not bic_value:
                bic_syrx_num = syrx_num
                bic_ppsn = row_dict['ppsn']
                bic_value = row_dict['consumption']
                bic_hours = row_dict['hours']
            elif row_dict['ppsn'] < bic_ppsn:
                bic_syrx_num = syrx_num
                bic_ppsn = row_dict['ppsn']
                bic_value = row_dict['consumption']
                bic_hours = row_dict['hours']

            row_dict_list.append(row_dict)

    # using the bic_syrx_num, find the difference for each other component
    for row in row_dict_list:
        new_row = calculate_final_row_values(bic_syrx_num, bic_value, bic_hours, row, price)
        # update final rows value
        rows.append(new_row)

    return rows


def generate_comparison_pdf(config, comparison_data, comparison_table_data, submitted_by, submitted_to):
    report_path = DataReports.generate_component_comparison_report(config, comparison_data, comparison_table_data,
                                                                   submitted_by, submitted_to)
    return report_path


@ReportingComponentsBlueprint.route("/api/ReportingComponents/GetComparisonPDFReport", methods=["POST"])
@from_request_body("config", ComponentReportingComparisonConfiguration)
@login_required
def get_comparison_pdf_report(config):
    if not config.submitted_to:
        return abort(409)

    submitted_by = g.uow.users.get_user_by_id(session["current_user"]["id"])
    submitted_to = config.submitted_to

    # get the submitted by and submitted to
    submitted_by, submitted_to = SharedReporting.get_submitted_contacts(submitted_by, submitted_to, g)

    total_energy_chart_info = TotalEnergyDataContainer()

    report_name = "Component Comparison Report"
    total_energy_chart_info.y_axis_label = "Energy Consumption (BTU)"
    total_energy_chart_info.title = "Intensity"
    comparison_data = get_comparison_chart_data(config)
    comparison_table_data = get_comparison_table_data(config, config.comparison_year)
    report_path = generate_comparison_pdf(config, comparison_data, comparison_table_data, submitted_by, submitted_to)

    return send_file(report_path, mimetype='application/pdf', as_attachment=True, attachment_filename=report_name + '.pdf')


def get_difference_data_for_year(syrx_nums, year, label):
    """
    Gets the difference data for a component and it's master points for a given year
    :param syrx_nums: Component's master points
    :param year: year to get data for
    :param label: series name label
    :return: returns a list of an object in the form of [{"name", "data"}]
    """
    # get the report year data for each master point
    data = g.uow.compiled_point_records.get_data_for_syrx_nums(syrx_nums, year, 1, 12)

    if len(data) > 0:
        # overwrite the name of the point with the name of the component
        data[0]["name"] = label
    else:
        # create an empty object to prevent an error
        data = [{"name": label,
                 "data": []}]
    return data


def map_difference_data(report_data, benchmark_data):
    """
    Creates a list of dictionaries from the report data and benchmark data
    :param report_data: data formatted for kendo in the format [{'name', 'data'}]
    :param benchmark_data: ''
    :return: list of dictionaries in the form [{'temp', 'report_value', 'benchmark_value'}, ...]
    """
    # map the data in each year to a dictionary
    list_by_temp = []
    x_values = []
    for report_entry in report_data[0]["data"]:
        list_by_temp.append({'temp': report_entry[0], 'report_value': report_entry[1], 'benchmark_value': 0})
        x_values.append(report_entry[0])

    for benchmark_entry in benchmark_data[0]["data"]:
        # if the value is in the list already, add a benchmark value to it
        if benchmark_entry[0] in x_values:
            entry = (record for record in list_by_temp if record["temp"] == benchmark_entry[0]).next()
            entry['benchmark_value'] = benchmark_entry[1]
        else:
            list_by_temp.append({'temp': benchmark_entry[0], 'report_value': 0, 'benchmark_value': benchmark_entry[1]})

    return list_by_temp


def calculate_difference(list_by_temp):
    """
    Calculates the difference between the report year data and benchmark year data
    :param list_by_temp: list of dictionaries by temperature
    :return: list of kendo-formatted dictionaries for the data for the difference charts
    """
    # find the difference between each year value
    difference_report_data = []
    difference_benchmark_data = []
    return_list = []

    for record in list_by_temp:
        difference_report_data.append([record["temp"], record["report_value"] - record["benchmark_value"]])
        difference_benchmark_data.append([record['temp'], 0])

    # add the differences to the series
    return_list.append({'name': 'Reported Consumption',
                        'data': difference_report_data})
    return_list.append({'name': 'Benchmark Consumption',
                        'data': difference_benchmark_data})

    return return_list


def get_difference_chart_data(config, entity):
    """
    Gets a ComponentDifferenceDataContainer that holds information for the chart
    :param config: ComponentReportingDifferenceConfiguration
    :param entity: Selected entity to get data for
    :return: ComponentDifferenceDataContainer that holds all information for the chart
    """
    consumption_series_list = []
    difference_series_list = []

    # get syrx numbers for entity
    syrx_nums = get_syrx_nums_from_entity(entity)

    # get label for entity
    label = get_label_for_entity(entity)

    if syrx_nums:
        # get data for the report year and benchmark year independently
        report_data = get_difference_data_for_year(syrx_nums, config.report_year, 'Reported Consumption')
        consumption_series_list += report_data
        benchmark_data = get_difference_data_for_year(syrx_nums, config.benchmark_year, 'Benchmark Consumption')
        consumption_series_list += benchmark_data

        list_by_temp = map_difference_data(report_data, benchmark_data)

        # sort the list by temperature
        list_by_temp = sorted(list_by_temp, key=lambda x: x['temp'])

        # find the differences
        difference_series_list += calculate_difference(list_by_temp)

    chart_info = ComponentDifferenceDataContainer()
    chart_info.component_description = label
    chart_info.title = "Intensity"
    chart_info.consumption_data = consumption_series_list
    chart_info.difference_data = difference_series_list
    chart_info.x_axis_label = "Temperature (F)"
    chart_info.y_axis_label = "Energy Consumption (BTU)"

    return chart_info


@ReportingComponentsBlueprint.route("/api/ReportingComponents/DifferenceChart", methods=["POST"])
@from_request_body("config", ComponentReportingDifferenceConfiguration)
@login_required
def get_difference_chart(config):
    if not config.selected_component:
        abort(409)

    final_data = get_difference_chart_data(config, config.selected_component)
    return json.dumps(final_data.__dict__)


def generate_difference_pdf(config, difference_data, comparison_table_data, submitted_by, submitted_to):
    report_path = DataReports.generate_component_difference_report(config, difference_data, comparison_table_data,
                                                                   submitted_by, submitted_to)
    return report_path


@ReportingComponentsBlueprint.route("/api/ReportingComponents/DifferencePDFReport", methods=["POST"])
@from_request_body("config", ComponentReportingDifferenceConfiguration)
@login_required
def get_component_difference_pdf_report(config):
    if not config.submitted_to:
        return abort(409)

    submitted_by = g.uow.users.get_user_by_id(session["current_user"]["id"])
    submitted_to = config.submitted_to

    # get the submitted by and submitted to
    submitted_by, submitted_to = SharedReporting.get_submitted_contacts(submitted_by, submitted_to, g)

    total_energy_chart_info = TotalEnergyDataContainer()

    report_name = "Component Difference Report"
    total_energy_chart_info.y_axis_label = "Energy Consumption (BTU)"
    total_energy_chart_info.title = "Intensity"
    difference_data = []
    for component_id in config.component_ids:
        difference_data.append(get_difference_chart_data(config, component_id))
    comparison_table_data = get_comparison_table_data(config, config.report_year)
    report_path = generate_difference_pdf(config, difference_data, comparison_table_data, submitted_by, submitted_to)

    return send_file(report_path, mimetype='application/pdf', as_attachment=True, attachment_filename=report_name + '.pdf')


def format_equipment_difference_data(data, label):
    if len(data) > 0:
        # overwrite the name of the point
        data[0]["name"] = label
    else:
        # create an empty object to prevent an error
        data = [{"name": label,
                 "data": []}]
    return data


def convert_values(report_data, conversion_factor):
    """
    Converts all of the averages for each temperature to the correct units
    :param report_data: report data list [{name:'' , data: []}]
    :param conversion_factor: factor to get the data in the right units
    :return: updates report data object
    """
    new_report_data = report_data[0]
    for i in range(len(report_data[0]['data'])):
        # get the list from the report data, should be in the format [x-value, y-value]
        entry = report_data[0]['data'][i]
        new_report_data['data'][i] = [entry[0], entry[1] * conversion_factor]
    return [new_report_data]


def get_y_axis_and_conversion_factor(config):
    """
    Gets the y axis unit and conversion factor
    :param config: EquipmentReport
    :return: y_axis_unit, conversion_factor
    """
    y_axis_units = "Btu"

    same_unit = g.uow.equipment.all_of_same_unit(config.syrx_nums)

    # if all equipment points have the same unit, then we will use that unit as the y axis
    if same_unit:
        y_axis_units = g.uow.equipment.get_equipment_point_by_syrx_num(config.syrx_nums[0])

        if 'units' in y_axis_units:
            y_axis_units = y_axis_units['units']
        else:
            y_axis_units = "Binary"

        # if the unit is kWh then have a conversion factor, otherwise it will be 1
        if y_axis_units.lower() == "kwh":
            conversion_factor = SharedReporting.get_factor('kwh', 'sum_btu')
        else:
            conversion_factor = 1.0
    else:
        # otherwise, we keep the units in Btu
        conversion_factor = 1.0

    return y_axis_units, conversion_factor


def convert_dict_to_list(consumption_series_dict):
    """
    Converts a dictionary of {x:y} coordinates to a list in the form [[x, y], [x, y], ...]
    :param consumption_series_dict:
    :return: list in the form
    """
    new_list = []
    for key in sorted(consumption_series_dict.keys()):
        new_list.append([key, consumption_series_dict[key]])
    return [{
        'data': new_list,
        'name': None
    }]


def get_consumption_data_for_year(syrx_num, year, start_month, end_month, conversion_factor):
    # get the data for the syrx number
    syrx_series = g.uow.compiled_point_records.get_data_for_syrx_nums([syrx_num], year, start_month, end_month)

    if len(syrx_series) > 0:
        # convert the data to new values
        convert_data_to_btu_unit(syrx_series[0]['data'], conversion_factor)

    return syrx_series


def calculate_difference_equipment_report(report_series_dict, benchmark_series_dict):
    """
    Calculates differences between report year and benchmark year
    :param report_series_dict: dict of values keyed by temp
    :param benchmark_series_dict:  dict of values keyed by temp
    :return: report_year_difference, benchmark_year_difference
    """
    report_diff_dict = {}
    benchmark_diff_dict = {}
    for key in report_series_dict:
        if key in benchmark_series_dict:
            report_diff_dict[key] = benchmark_series_dict[key] - report_series_dict[key]
            benchmark_diff_dict[key] = 0
        else:
            report_diff_dict[key] = 0 - report_series_dict[key]
            benchmark_diff_dict[key] = 0

    return report_diff_dict, benchmark_diff_dict


def get_syrx_data(config):
    """
    Gets the data for the syrx number in config and returns a kendo-formatted object of the data
    :param config: EquipmentReport
    :return:
    """
    report_series_dict = {}
    benchmark_series_dict = {}

    if len(config.syrx_nums) > 1:
        target_unit = "mmbtu"
    else:
        target_unit = None

    for syrx_num in config.syrx_nums:
        # get the equipment point
        ep = g.uow.equipment.get_equipment_point_by_syrx_num(syrx_num)

        if not target_unit:
            target_unit = ep['units'].lower()

        conversion_factor = SharedReporting.get_component_point_conversion(ep['units'].lower(), 'mmbtu')

        syrx_series = get_consumption_data_for_year(syrx_num, config.report_year, config.start_month, config.end_month,
                                                    conversion_factor)
        # add to the existing series
        add_to_new_series_data(report_series_dict, syrx_series[0]['data'])

        syrx_series_benchmark = get_consumption_data_for_year(syrx_num, config.comparison_year, config.start_month,
                                                              config.end_month, conversion_factor)

        # add to the existing series
        add_to_new_series_data(benchmark_series_dict, syrx_series_benchmark[0]['data'])

    report_difference_list, benchmark_difference_list = calculate_difference_equipment_report(report_series_dict,
                                                                                              benchmark_series_dict)

    consumption_series_list = convert_dict_to_list(report_series_dict)
    consumption_series_list[0]['name'] = 'Reported Consumption'
    benchmark_series_list = convert_dict_to_list(benchmark_series_dict)
    consumption_series_list += benchmark_series_list
    consumption_series_list[1]['name'] = 'Benchmark Consumption'

    difference_series_list = convert_dict_to_list(report_difference_list)
    difference_series_list[0]['name'] = 'Reported Consumption'
    difference_series_list += convert_dict_to_list(benchmark_difference_list)
    difference_series_list[1]['name'] = 'Benchmark Consumption'

    chart_info = ComponentDifferenceDataContainer()
    chart_info.component_description = ""
    chart_info.title = "Intensity"
    chart_info.consumption_data = consumption_series_list
    chart_info.difference_data = difference_series_list
    chart_info.x_axis_label = "Temperature (F)"
    chart_info.y_axis_label = "Energy Consumption (" + SharedReporting.get_y_unit_label(target_unit.lower()) + ")"
    return chart_info


@ReportingComponentsBlueprint.route("/api/ReportingComponents/EquipmentReport", methods=["POST"])
@from_request_body("config", EquipmentReport)
@login_required
def get_equipment_report(config):
    if not config.syrx_num:
        return abort(400)
    elif not config.report_year:
        return abort(400)
    elif not config.comparison_year:
        return abort(400)

    if config.syrx_num == "all":
        # get the the consumption for each equipment point
        equipment_points = g.uow.equipment.get_equipment_reporting_points(config.equipment_id)
        syrx_nums = map(lambda x: x['id'], equipment_points)

        config.syrx_nums = syrx_nums
    else:
        # only one syrx number
        config.syrx_nums = [config.syrx_num]

    # get the data for the report year and comparison year for the syrx num
    equipment_data = get_syrx_data(config)
    return json.dumps(equipment_data.__dict__)


def get_total_energy_data_for_year(config, equipment_point):
    """
    Sums the energy data for each equipment point together for the entire year
    :param config: EquipmentReport
    :param equipment_point: current equipment point to process
    """
    report_year_sum = g.uow.compiled_point_records.get_year_consumption_data_for_points([equipment_point],
                                                                                        config.report_year)
    if 'sum_value' in report_year_sum:
        report_year_sum = report_year_sum['sum_value']
    else:
        report_year_sum = 0

    benchmark_year_sum = g.uow.compiled_point_records.get_year_consumption_data_for_points([equipment_point],
                                                                                           config.comparison_year)
    if 'sum_value' in benchmark_year_sum:
        benchmark_year_sum = benchmark_year_sum['sum_value']
    else:
        benchmark_year_sum = 0

    return report_year_sum, benchmark_year_sum


def get_total_energy_data_for_month(config, equipment_point):
    """
    Sums the energy data for each equipment point together for the current month in the year
    :param config: EquipmentReport
    :param equipment_point: list of equipment points
    :return:
    """
    report_year_month_data = g.uow.compiled_point_records.get_month_consumption_data_for_points([equipment_point], config.report_year)
    benchmark_year_month_data = g.uow.compiled_point_records.get_month_consumption_data_for_points([equipment_point], config.comparison_year)
    if 'sum_value' in report_year_month_data:
        report_year_month_data = report_year_month_data['sum_value']
    else:
        report_year_month_data = 0

    if 'sum_value' in benchmark_year_month_data:
        benchmark_year_month_data = benchmark_year_month_data['sum_value']
    else:
        benchmark_year_month_data = 0

    return report_year_month_data, benchmark_year_month_data


def find_price_for_equipment_points(units, equipment_id):
    """
    Finds the price/unit of the equipment points based on unit
    :param units: 'kwh'/'btu'/'mcf'
    :param equipment_id: Equipment id to find price based on
    :return:
    """
    # find the equipment, which will help find the group
    equipment = g.uow.equipment.get_by_id(equipment_id)

    if units == 'kwh':
        acct = 'electric'
    else:
        acct = 'gas'
    account = SharedReporting.get_first_account_for_group_of_type(equipment.group_id, acct, g.uow)
    price = g.uow.price_normalizations.get_most_recent_for_account(account['id'])
    # ensure the price was found
    if price:
        price = price.value
    else:
        price = 0
    return price


def set_monthly_values(ret_obj, monthly_report_year_sum, monthly_benchmark_year_sum, price, units, conversion_factor):
    """
    Sets the monthly values on the return object
    :param ret_obj: object containing all of the data
    :param monthly_report_year_sum: sum of the report-year-current-month-consumption
    :param monthly_benchmark_year_sum: sum of the benchmark-year-current-month-consumption
    :param price: price/unit
    :param units: units the data is measured in
    :param conversion_factor: conversion factor to btu's
    """
    ret_obj['report_consumption_month'] = monthly_report_year_sum * conversion_factor
    ret_obj['benchmark_consumption_month'] = monthly_benchmark_year_sum * conversion_factor

    ret_obj['difference_month'] = monthly_benchmark_year_sum - monthly_report_year_sum

    # get the percentage change
    if monthly_benchmark_year_sum == 0:
        ret_obj['percent_month'] = "{:.2f}".format(0.0)
    else:
        ret_obj['percent_month'] = "{:.2f}".format((ret_obj['difference_month'] * 1.0 /
                                                    monthly_benchmark_year_sum) * 100.0)

    # get the cost difference
    report_cost = monthly_report_year_sum * price
    benchmark_cost = monthly_benchmark_year_sum * price

    ret_obj['cost_month'] = benchmark_cost - report_cost


def set_yearly_values(ret_obj, report_year_sum, benchmark_year_sum, price, units, conversion_factor):
    """
    Sets the yearly values on the return object
    :param ret_obj: object containing all of the data
    :param report_year_sum: sum of the report-year-consumption
    :param benchmark_year_sum: sum of the benchmark-year-consumption
    :param price: price/unit
    :param units: units the data is measured in
    :param conversion_factor: Conversion factor to get unit to BTU's
    """
    ret_obj['report_consumption_year'] = report_year_sum * conversion_factor
    ret_obj['benchmark_consumption_year'] = benchmark_year_sum * conversion_factor

    ret_obj['difference_year'] = benchmark_year_sum - report_year_sum

    # get the percentage change
    if benchmark_year_sum == 0:
        ret_obj['percent_year'] = "{:.2f}".format(0.0)
    else:
        ret_obj['percent_year'] = "{:.2f}".format((ret_obj['difference_year'] * 1.0 / benchmark_year_sum) * 100.0)

    # get the cost difference
    report_cost = report_year_sum * price
    benchmark_cost = benchmark_year_sum * price

    ret_obj['cost_year'] = benchmark_cost - report_cost


def calculate_totals_for_report(config, units, price, equipment_point, conversion_factor):
    """
    Calculates the monthly and yearly totals for report year and benchmark year
    :param config: EquipmentReport
    :param units: 'kwh'/'btu'/'mcf'
    :param price: price/unit
    :param equipment_point: list of equipment points to get data for
    :param conversion_factor: conversion factor to get to BTU's
    :return: object containing the totals for each month, year, and cost/each
    """
    ret_obj = {
        'report_consumption_month': 0,
        'benchmark_consumption_month': 0,
        'report_consumption_year': 0,
        'benchmark_consumption_year': 0,
        'difference_month': 0,
        'difference_year': 0,
        'percent_month': 0,
        'percent_year': 0,
        'cost_month': 0,
        'cost_year': 0
    }

    monthly_report_year_sum, monthly_benchmark_year_sum = get_total_energy_data_for_month(config, equipment_point)
    set_monthly_values(ret_obj, monthly_report_year_sum, monthly_benchmark_year_sum, price, units, conversion_factor)

    report_year_sum, benchmark_year_sum = get_total_energy_data_for_year(config, equipment_point)
    set_yearly_values(ret_obj, report_year_sum, benchmark_year_sum, price, units, conversion_factor)

    return ret_obj


@ReportingComponentsBlueprint.route("/api/ReportingComponents/EquipmentReportTable", methods=["POST"])
@from_request_body("config", EquipmentReport)
@login_required
def get_equipment_report_table(config):
    # get the reporting points (that can be converted to btu)
    equipment_points = g.uow.equipment.get_equipment_reporting_points(config.equipment_id)

    ret_obj = {
        'report_consumption_month': 0,
        'benchmark_consumption_month': 0,
        'report_consumption_year': 0,
        'benchmark_consumption_year': 0,
        'difference_month': 0,
        'difference_year': 0,
        'percent_month': 0,
        'percent_year': 0,
        'cost_month': 0,
        'cost_year': 0
    }

    # get the price for calculating cost savings
    price = find_price_for_equipment_points('mmbtu', config.equipment_id)

    # if they are all the same, find the price/unit
    for equipment_point in equipment_points:
        ep = g.uow.equipment.get_equipment_point_by_syrx_num(equipment_point['id'])
        conversion_factor = SharedReporting.get_component_point_conversion(ep['units'].lower(), 'mmbtu')

        temp_obj = calculate_totals_for_report(config, ep['units'], price, ep, conversion_factor)

        # update the ret_obj with the values
        ret_obj['report_consumption_month'] += temp_obj['report_consumption_month']
        ret_obj['benchmark_consumption_month'] += temp_obj['benchmark_consumption_month']
        ret_obj['report_consumption_year'] += temp_obj['report_consumption_year']
        ret_obj['benchmark_consumption_year'] += temp_obj['benchmark_consumption_year']
        ret_obj['cost_month'] += temp_obj['cost_month']
        ret_obj['cost_year'] += temp_obj['cost_year']

    # calculate final difference and percent difference
    ret_obj['difference_month'] = ret_obj['benchmark_consumption_month'] - ret_obj['report_consumption_month']
    ret_obj['difference_year'] = ret_obj['benchmark_consumption_year'] - ret_obj['report_consumption_year']

    if ret_obj['benchmark_consumption_month'] == 0:
        ret_obj['percent_month'] = "{:.2f}".format(0.0)
    else:
        ret_obj['percent_month'] = "{:.2f}".format((ret_obj['difference_month'] * 1.0 /
                                                    ret_obj['benchmark_consumption_month']) * 100.0)

    if ret_obj['benchmark_consumption_year'] == 0:
        ret_obj['percent_year'] = "{:.2f}".format(0.0)
    else:
        ret_obj['percent_year'] = "{:.2f}".format((ret_obj['difference_year'] * 1.0 /
                                                   ret_obj['benchmark_consumption_year']) * 100.0)

    # format the cost savings
    ret_obj['cost_month'] = "${:,.2f}".format(ret_obj['cost_month'])
    ret_obj['cost_year'] = "${:,.2f}".format(ret_obj['cost_year'])

    # format consumption numbers
    ret_obj['report_consumption_month'] = "{:,.2f}".format(ret_obj['report_consumption_month'])
    ret_obj['report_consumption_year'] = "{:,.2f}".format(ret_obj['report_consumption_year'])
    ret_obj['benchmark_consumption_month'] = "{:,.2f}".format(ret_obj['benchmark_consumption_month'])
    ret_obj['benchmark_consumption_year'] = "{:,.2f}".format(ret_obj['benchmark_consumption_year'])
    ret_obj['difference_month'] = "{:,.2f}".format(ret_obj['difference_month'])
    ret_obj['difference_year'] = "{:,.2f}".format(ret_obj['difference_year'])

    return json.dumps(ret_obj)
