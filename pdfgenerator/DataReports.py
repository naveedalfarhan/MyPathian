from datetime import datetime
import json
import tempfile
import shutil
import collections
import subprocess
import locale
import os
import pkg_resources
from pdb import set_trace as trace

from api.models.ImageGeneratorThread import ImageGeneratorThread
from api.models.PygalConfig import ChartConfig


report_templates_package = "report_templates"

def intround(value):
    return int(round(value))

def format_currency(value):
    # set the locale
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    return locale.currency(value, grouping=True)

class DataReports:

    @classmethod
    def __create_temp_dir(cls, report_options, file_paths_to_copy, images=[]):
        temp_dir = tempfile.mkdtemp()

        # this loop copies all of the images' files to the temp directory
        # that was just created
        for image in images:
            name = image["name"]
            file_path = image["file_path"]
            new_path = os.path.join(temp_dir, name)

            # copy the image file
            shutil.copyfile(file_path, new_path)

        # write out data.js file
        path_to_js_file = os.path.join(temp_dir, "data.js")
        fo = open(path_to_js_file, "w+")
        javascript = "window['report_options'] = " + json.dumps(report_options) + ";"
        fo.write(javascript)
        fo.close()

        # copy all of the required html/js/css files into the temp directory
        for file_path in file_paths_to_copy:
            shutil.copy(file_path, temp_dir)

        return temp_dir

    @classmethod
    def generate_component_standards_report(cls, config, standards_chart_info, standards_table_info, submitted_by, submitted_to):
        # build report options
        report_options = {
            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "Component Standards Report",
            "submittedto": submitted_to,
            "submittedby": submitted_by,
            "reportyear": config.report_year,
            "standardschartsrc": "standards_chart.svg",
            "standardstable": standards_table_info
        }

        images = []

        # create a temporary directory for the different threads to use
        chart_temp_dir = tempfile.mkdtemp()

        standards_chart_config = ChartConfig

        # set the title and axis titles
        standards_chart_config.title = "Intensity"
        standards_chart_config.x_title = standards_chart_info.x_axis_label
        standards_chart_config.y_title = "Energy Intensity (BTU/sqft)"

        # change the height and width
        standards_chart_config.height = 700
        standards_chart_config.width = 700

        # create and start the thread that will create the image
        standards_name = "standards_chart.svg"
        standards_thread = ImageGeneratorThread(standards_chart_config, standards_chart_info.data, chart_temp_dir, standards_name)
        standards_thread.start()
        standards_thread.join()
        images.append({"name": standards_name, "file_path": os.path.join(chart_temp_dir, standards_thread.image_name)})

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "component_standards"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy, images)

        # delete chart temporary directory
        shutil.rmtree(chart_temp_dir)

        pdfname = "consumption_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath


    @classmethod
    def generate_consumption_report(cls, report_year, benchmark_year, intensity_chart_info, total_energy_chart_info, total_energy_table_info, submitted_by_user, submitted_to, units):
        # build report options
        report_options = {
            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "Consumption Report",
            "submittedto": submitted_to,
            "submittedby": submitted_by_user,
            "reportyear": report_year,
            "benchmarkyear": benchmark_year,
            "AvgUnitReduction": "",
            "Units": units,
            "AvgCostReduction": "",
            "intensitychartsrc": "intensity_chart.svg",
            "datatable": [
            ],
            "charts": [
            ]
        }
        series_data = []

        # in order to insert table data in proper order, it must be ordered by year
        # python does not support ordered dictionaries by default, so we import OrderedDict
        od = collections.OrderedDict(sorted(total_energy_table_info.items()))
        total_utility = 0
        total_reported = 0
        total_benchmark = 0
        total_cost_reduction = 0
        for year in od:
            utility = 0
            benchmark = 0
            reported = 0
            cost_reduction = 0

            # loop through each group in each year and append to table data
            for entry in od[year]:
                report_options['datatable'].append({'entity': entry['entity'],
                                                    'utility': "{:,d}".format(intround(entry['data']['utility'])),
                                                    'reported': "{:,d}".format(intround(entry['data']['reported'])),
                                                    'benchmark': "{:,d}".format(intround(entry['data']['benchmark'])),
                                                    'difference': "{:,d}".format(intround(entry['data']['difference'])),
                                                    'change': "{:,.2f}%".format(float(entry['data']['change'])),
                                                    'savings': format_currency(intround(entry['data']['cost_reduction'])),
                                                    'type': 'normal'})

                # increase the total utility, reported, and benchmark for the given year
                utility += entry['data']['utility']
                reported += entry['data']['reported']
                benchmark += entry['data']['benchmark']
                cost_reduction += entry['data']['cost_reduction']


            # calculate difference and change for the year
            difference = benchmark - reported
            if benchmark != 0:
                change = difference * 1.0 / benchmark * 100
            else:
                change = 0

            # add year subtotal record to table data
            report_options['datatable'].append({'entity': str(year) + " Total",
                                                'utility': "{:,d}".format(intround(utility)),
                                                'reported': "{:,d}".format(intround(reported)),
                                                'benchmark': "{:,d}".format(intround(benchmark)),
                                                'difference': "{:,d}".format(intround(difference)),
                                                'change': "{:,.2f}%".format(change),
                                                'savings': format_currency(intround(cost_reduction)),
                                                'type': 'subtotal'})

            if report_year == year:
                # reduction = <report year benchmark> /  <reporting entities>
                report_options['AvgUnitReduction'] = intround(difference) / len(intensity_chart_info.data)
                report_options['AvgCostReduction'] = format_currency(intround(cost_reduction) / len(intensity_chart_info.data))

            # increase total energy for all years
            total_utility += utility
            total_reported += reported
            total_benchmark += benchmark
            total_cost_reduction += cost_reduction

        # calculate difference and change for all years
        total_difference = total_benchmark - total_reported
        if total_benchmark != 0:
            total_change = total_difference * 1.0 / total_benchmark * 100
        else:
            total_change = 0

        # add grand totals to the table data
        report_options['datatable'].append({'entity': 'Grand Total',
                                           'utility': "{:,d}".format(intround(total_utility)),
                                           'reported': "{:,d}".format(intround(total_reported)),
                                           'benchmark': "{:,d}".format(intround(total_benchmark)),
                                           'difference': "{:,d}".format(intround(total_difference)),
                                           'change': "{:,.2f}%".format(total_change),
                                           'savings': format_currency(intround(total_cost_reduction)),
                                           'type': 'total'})

        for group_record in intensity_chart_info.data:
            series_data.append(
                {
                    "name": group_record['name'] + " - " + str(report_year),
                    "data": group_record['data']
                }
            )

        # create a temporary directory for the different threads to use
        chart_temp_dir = tempfile.mkdtemp()

        intensity_chart_config = ChartConfig

        # set the title and axis titles
        intensity_chart_config.title = "Intensity"
        intensity_chart_config.x_title = total_energy_chart_info.x_axis_label
        intensity_chart_config.y_title = "Energy Intensity (BTU/sqft)"

        # change the height and width
        intensity_chart_config.height = 700
        intensity_chart_config.width = 700

        # create and start the thread that will create the image
        intensity_name = "intensity_chart.svg"
        intensity_thread = ImageGeneratorThread(intensity_chart_config, series_data, chart_temp_dir, intensity_name)
        intensity_thread.start()

        # build array of images... the "name" property is what will be passed
        # into the javascript file, the "file" property is the file handle
        # returned by the renderer
        images = []

        # get consumption chart images and difference chart images
        account_counter = 0
        for record in total_energy_chart_info.data:
            for year_data in record['data']:
                account_counter += 1
                # consumption image for account
                series_data1 = [
                    {
                        "name": "Reported Consumption",
                        "data": year_data.reported_consumption
                    },
                    {
                        "name": "Benchmark Consumption",
                        "data": year_data.benchmark_consumption
                    }
                ]

                config = ChartConfig

                config.title = total_energy_chart_info.title
                config.x_title = total_energy_chart_info.x_axis_label
                config.y_title = total_energy_chart_info.y_axis_label
                config.legend_at_bottom = True

                temp_name = "image" + str(account_counter) + "-1.svg"
                image_thread_1 = ImageGeneratorThread(config, series_data1, chart_temp_dir, temp_name)
                image_thread_1.start()

                #difference image for account
                series_data2 = [
                    {
                        "name": "Reported Consumption",
                        "data": year_data.diff
                    },
                    {
                        "name": "Benchmark Consumption",
                        "data": year_data.benchmark_diff
                    }
                ]

                temp_name_2 = "image" + str(account_counter) + "-2.svg"
                image_thread_2 = ImageGeneratorThread(config, series_data2, chart_temp_dir, temp_name_2)
                image_thread_2.start()



                report_options['charts'].append(
                    {
                        "entityname": record['entity'],
                        "accountname": year_data.account_name,
                        "year": year_data.year,
                        "energyreduction":"{:,.2f}".format(year_data.difference),
                        "costreduction": format_currency(year_data.cost_reduction),
                        "chartscalculatedat": "${:,.3f}".format(year_data.calculated_at),
                        "chart1url": temp_name,
                        "chart2url": temp_name_2
                    })

                image_thread_1.join()
                image_thread_2.join()
                images.append({"name": temp_name, "file_path": os.path.join(chart_temp_dir, image_thread_1.image_name)})
                images.append({"name": temp_name_2, "file_path": os.path.join(chart_temp_dir, image_thread_2.image_name)})

        intensity_thread.join()
        images.append({"name": intensity_name, "file_path": os.path.join(chart_temp_dir, intensity_thread.image_name)})

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "consumption"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy, images)

        # delete chart temporary directory
        shutil.rmtree(chart_temp_dir)

        pdfname = "consumption_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath

    @classmethod
    def generate_variance_report(cls, data, report_year, benchmark_year, submitted_by_user, submitted_to):
        # build report options
        report_options = {

            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": 'Variance Report',
            "submittedto": submitted_to,
            "submittedby": submitted_by_user,
            "reportyear": report_year,
            "benchmarkyear": benchmark_year,
            "sites": data
        }

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "variance"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy)

        pdfname = "variance_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-O', 'Landscape', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath

    @classmethod
    def generate_consumptiontext_report(cls, report_year, benchmark_year, report, submitted_by_user, account_type):
        # build report options
        report_options = {

            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "Consumption Text Report",
            "submittedto": "",
            "submittedby": submitted_by_user,
            "reportyear": report_year,
            "benchmarkyear": benchmark_year,
            "reportdata": report,
            "accounttype": account_type

        }

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "consumptiontext"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy)

        pdfname = "consumptiontext_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")
        subprocess.call(['C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm', '--header-html', header_html_path, '--footer-html', footer_html_path, 'cover', cover_html_path, report_html_path, pdfpath])
        #subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm','--header-html', header_html_path, '--footer-html', footer_html_path,'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath

    @classmethod
    def generate_kvarh_report(cls, report_year, benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to):
        images = []
        # build report options
        report_options = {

            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "kVArh Report",
            "submittedto": submitted_to,
            "submittedby": submitted_by_user,
            "reportyear": report_year,
            "benchmarkyear": benchmark_year,
            "charts": [
            ]
        }

        # create temporary directory for svg generation
        chart_temp_dir = tempfile.mkdtemp()

        # get consumption chart images and difference chart images
        account_counter = 0
        for record in total_energy_chart_info.data:
            for year_data in record['data']['chart_data']:
                account_counter += 1
                # consumption image for account
                series_data1 = [
                    {
                        "name": "Reported Consumption",
                        "data": year_data.reported_consumption
                    },
                    {
                        "name": "Benchmark Consumption",
                        "data": year_data.benchmark_consumption
                    }
                ]

                # configure the chart and send to a separate thread to be generated
                config = ChartConfig

                config.title = total_energy_chart_info.title
                config.x_title = total_energy_chart_info.x_axis_label
                config.y_title = total_energy_chart_info.y_axis_label
                config.legend_at_bottom = True

                # create a name for the image, then send to the new thread to generate chart
                temp_name = "image" + str(account_counter) + "-1.svg"
                image_thread_1 = ImageGeneratorThread(config, series_data1, chart_temp_dir, temp_name)
                image_thread_1.start()

                #difference image for account
                series_data2 = [
                    {
                        "name": "Reported Consumption",
                        "data": year_data.diff
                    },
                    {
                        "name": "Benchmark Consumption",
                        "data": year_data.benchmark_diff
                    }
                ]

                temp_name_2 = "image" + str(account_counter) + "-2.svg"
                image_thread_2 = ImageGeneratorThread(config, series_data2, chart_temp_dir, temp_name_2)
                image_thread_2.start()

                report_options['charts'].append(
                    {
                        "entityname": record['entity'],
                        "accountname": year_data.account_name,
                        "year": year_data.year,
                        "energyreduction": "{:,.2f}".format(year_data.difference),
                        "chart1url": temp_name,
                        "chart2url": temp_name_2
                    })

                # wait for both threads to finish, add the file handles to images, then move to the next 2 charts
                image_thread_1.join()
                image_thread_2.join()
                images.append({"name": temp_name, "file_path": os.path.join(chart_temp_dir, image_thread_1.image_name)})
                images.append({"name": temp_name_2, "file_path": os.path.join(chart_temp_dir, image_thread_2.image_name)})

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "kvarh"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy, images)

        pdfname = "kVArh_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath

    @classmethod
    def generate_powerfactor_report(cls, report_year, benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to):
        images = []

        # build report options
        report_options = {

            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "Power Factor Report",
            "submittedto": submitted_to,
            "submittedby": submitted_by_user,
            "reportyear": report_year,
            "benchmarkyear": benchmark_year,
            "charts": [
            ]
        }

        # create a temp directory for chart generation
        chart_temp_dir = tempfile.mkdtemp()

        # get consumption chart images and difference chart images
        account_counter = 0
        for record in total_energy_chart_info.data:
            for year_data in record['data']['chart_data']:
                account_counter += 1
                # consumption image for account
                series_data1 = [
                    {
                        "name": "Reported Consumption",
                        "data": year_data.reported_consumption
                    },
                    {
                        "name": "Benchmark Consumption",
                        "data": year_data.benchmark_consumption
                    }
                ]

                # configure the chart and send to a separate thread to be generated
                config = ChartConfig

                config.title = total_energy_chart_info.title
                config.x_title = total_energy_chart_info.x_axis_label
                config.y_title = total_energy_chart_info.y_axis_label
                config.legend_at_bottom = True

                # create a name for the image, then send to the new thread to generate chart
                temp_name = "image" + str(account_counter) + "-1.svg"
                image_thread_1 = ImageGeneratorThread(config, series_data1, chart_temp_dir, temp_name)
                image_thread_1.start()

                #difference image for account
                series_data2 = [
                    {
                        "name": "Reported Consumption",
                        "data": year_data.diff
                    },
                    {
                        "name": "Benchmark Consumption",
                        "data": year_data.benchmark_diff
                    }
                ]

                temp_name_2 = "image" + str(account_counter) + "-2.svg"
                image_thread_2 = ImageGeneratorThread(config, series_data2, chart_temp_dir, temp_name_2)
                image_thread_2.start()

                report_options['charts'].append(
                    {
                        "entityname": record['entity'],
                        "accountname": year_data.account_name,
                        "year": year_data.year,
                        "chart1url": temp_name,
                        "chart2url": temp_name_2
                    })

                # wait for both threads to finish, then add their file handles to images
                image_thread_1.join()
                image_thread_2.join()
                images.append({"name": temp_name, "file_path": os.path.join(chart_temp_dir, image_thread_1.image_name)})
                images.append({"name": temp_name_2, "file_path": os.path.join(chart_temp_dir, image_thread_2.image_name)})

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "powerfactor"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy, images)

        pdfname = "powerfactor_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath

    @classmethod
    def generate_peak_report(cls, data, report_year, submitted_by_user, submitted_to):
        # build report options
        report_options = {
            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "Peak Report",
            "submittedto": submitted_to,
            "submittedby": submitted_by_user,
            "sets": []
        }

        # create a temp directory for generating images
        chart_temp_dir = tempfile.mkdtemp()

        images = []
        counter = 0
        for entry in data:
            temp_series_data = [
                {
                    "name": "Hourly Temperature",
                    "data": entry['temp_data']
                }
            ]

            # configure the chart and send to a separate thread to be generated
            config = ChartConfig

            config.title = entry['date']
            config.x_title = "Hour"
            config.y_title = "Temperature (F)"
            config.legend_at_bottom = True

            config.width = 750
            config.height = 700

            # create a name for the image, then send to the new thread to generate chart
            temp_name = "image" + str(counter) + ".svg"
            image_thread_1 = ImageGeneratorThread(config, temp_series_data, chart_temp_dir, temp_name)
            image_thread_1.start()
            image_thread_1.join()
            counter += 1

            demand_series_data = [
                {
                    "name": "Hourly Consumption Rate",
                    "data": entry["demand_data"]
                }
            ]

            temp_name_2 = "image" + str(counter) + ".svg"

            config = ChartConfig
            config.y_title = "Electric Usage (kW)"

            image_thread_2 = ImageGeneratorThread(config, demand_series_data, chart_temp_dir, temp_name_2)
            image_thread_2.start()

            image_thread_2.join()
            images.append({"name": temp_name, "file_path": os.path.join(chart_temp_dir, image_thread_1.image_name)})
            images.append({"name": temp_name_2, "file_path": os.path.join(chart_temp_dir, image_thread_2.image_name)})

            counter += 1

            # create a new entry to add to the report options
            new_record = {
                'location': entry['entity'] + " - " + entry['account_name'],
                'date': entry['date'],
                'chart1': temp_name,
                'chart2': temp_name_2,
                'datatable': [
                ]
            }

            # add demand information to data table
            for demand_table_entry in entry['demand_table_data']:
                new_record['datatable'].append({'year': report_year,
                                                'kw': demand_table_entry[0],
                                                'date': demand_table_entry[1]})


            # add new record to sets
            report_options['sets'].append(new_record)


        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "peak"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy, images)

        pdfname = "peak_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath

    @classmethod
    def generate_kvah_report(cls, report_year, benchmark_year, total_energy_chart_info, submitted_by_user, submitted_to):
        images = []

        # build report options
        report_options = {

            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "kVAh Report",
            "submittedto": submitted_to,
            "submittedby": submitted_by_user,
            "reportyear": report_year,
            "benchmarkyear": benchmark_year,
            "charts": [
            ]
        }

        # create a temp directory for generating the consumption charts
        chart_temp_dir = tempfile.mkdtemp()

        # get consumption chart images and difference chart images
        account_counter = 0
        for record in total_energy_chart_info.data:
            for year_data in record['data']['chart_data']:
                account_counter += 1
                # consumption image for account
                series_data1 = [
                    {
                        "name": "Reported Consumption",
                        "data": year_data.reported_consumption
                    },
                    {
                        "name": "Benchmark Consumption",
                        "data": year_data.benchmark_consumption
                    }
                ]

                # configure the chart and send to a separate thread to be generated
                config = ChartConfig

                config.title = total_energy_chart_info.title
                config.x_title = total_energy_chart_info.x_axis_label
                config.y_title = total_energy_chart_info.y_axis_label
                config.legend_at_bottom = True

                # create a name for the image, then send to the new thread to generate chart
                temp_name = "image" + str(account_counter) + "-1.svg"
                image_thread_1 = ImageGeneratorThread(config, series_data1, chart_temp_dir, temp_name)
                image_thread_1.start()

                #difference image for account
                series_data2 = [
                    {
                        "name": "Reported Consumption",
                        "data": year_data.diff
                    },
                    {
                        "name": "Benchmark Consumption",
                        "data": year_data.benchmark_diff
                    }
                ]

                temp_name_2 = "image" + str(account_counter) + "-2.svg"
                image_thread_2 = ImageGeneratorThread(config, series_data2, chart_temp_dir, temp_name_2)
                image_thread_2.start()

                report_options['charts'].append(
                    {
                        "entityname": record['entity'],
                        "accountname": year_data.account_name,
                        "year": year_data.year,
                        "chart1url": temp_name,
                        "chart2url": temp_name_2
                    })

                # wait for both threads to be done and add their file handles to the images list
                image_thread_1.join()
                image_thread_2.join()
                images.append({"name": temp_name, "file_path": os.path.join(chart_temp_dir, image_thread_1.image_name)})
                images.append({"name": temp_name_2, "file_path": os.path.join(chart_temp_dir, image_thread_2.image_name)})

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "kvah"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy, images)

        pdfname = "kVAh_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath

    @classmethod
    def generate_component_comparison_report(cls, config, comparison_chart_data, comparison_table_data, submitted_by, submitted_to):
        # build report options
        report_options = {
            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "Component Comparison Report",
            "submittedto": submitted_to,
            "submittedby": submitted_by,
            "reportyear": config.comparison_year,
            "comparisonchartsrc": "comparison_chart.svg",
            "comparisontable": comparison_table_data
        }

        images = []

        # create a temporary directory for the different threads to use
        chart_temp_dir = tempfile.mkdtemp()

        comparison_chart_config = ChartConfig

        # set the title and axis titles
        comparison_chart_config.title = comparison_chart_data.title
        comparison_chart_config.x_title = comparison_chart_data.x_axis_label
        comparison_chart_config.y_title = comparison_chart_data.y_axis_label

        # change the height and width
        comparison_chart_config.height = 700
        comparison_chart_config.width = 700

        # create and start the thread that will create the image
        comparison_name = "comparison_chart.svg"
        comparison_thread = ImageGeneratorThread(comparison_chart_config, comparison_chart_data.data, chart_temp_dir, comparison_name)
        comparison_thread.start()
        comparison_thread.join()
        images.append({"name": comparison_name, "file_path": os.path.join(chart_temp_dir, comparison_thread.image_name)})

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "component_comparison"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]


        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy, images)

        # delete chart temporary directory
        shutil.rmtree(chart_temp_dir)

        pdfname = "consumption_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath

    @classmethod
    def generate_component_difference_report(cls, config, difference_chart_data, difference_table_data, submitted_by, submitted_to):
        # build report options
        report_options = {
            "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
            "reportname": "Component Difference Report",
            "submittedto": submitted_to,
            "submittedby": submitted_by,
            "reportyear": config.report_year,
            'benchmarkyear': config.benchmark_year,
            "differencetable": difference_table_data,
            "charts": []
        }

        images = []

        # create a temporary directory for the different threads to use
        chart_temp_dir = tempfile.mkdtemp()

        component_counter = 0
        # each entry in difference_chart_data is a ComponentDifferenceDataContainer
        for component_series in difference_chart_data:
            chart_config = ChartConfig

            chart_config.title = component_series.title
            chart_config.x_title = component_series.x_axis_label
            chart_config.y_title = component_series.y_axis_label
            chart_config.legend_at_bottom = True

            # consumption image for component
            temp_name = "image" + str(component_counter) + "-1.svg"
            image_thread_1 = ImageGeneratorThread(chart_config, component_series.consumption_data, chart_temp_dir, temp_name)
            image_thread_1.start()

            # difference image for component
            temp_name_2 = "image" + str(component_counter) + "-2.svg"
            image_thread_2 = ImageGeneratorThread(chart_config, component_series.difference_data, chart_temp_dir, temp_name_2)
            image_thread_2.start()

            # add metadata to the charts list
            report_options['charts'].append({
                'component_description': component_series.component_description,
                'chart1url': temp_name,
                'chart2url': temp_name_2
            })

            # make sure all threads are stopped
            image_thread_1.join()
            image_thread_2.join()
            images.append({"name": temp_name, "file_path": os.path.join(chart_temp_dir, image_thread_1.image_name)})
            images.append({"name": temp_name_2, "file_path": os.path.join(chart_temp_dir, image_thread_2.image_name)})

        # this is a list of all of the static files necessary to generate the pdf
        package_subfile = "component_difference"
        file_paths_to_copy = [
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "cover-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "footer-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "header-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report.html")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "report-populate.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join(package_subfile, "template.css")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("images", "PathianLogoSmall.png")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "jquery.min.js")),
            pkg_resources.resource_filename(report_templates_package, os.path.join("scripts", "wkhtmltopdf.substitutions.js"))
        ]

        temp_dir = cls.__create_temp_dir(report_options, file_paths_to_copy, images)

        # delete chart temporary directory
        shutil.rmtree(chart_temp_dir)

        pdfname = "consumption_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
        pdfpath = os.path.join(temp_dir, pdfname)
        header_html_path = os.path.join(temp_dir, "header.html")
        footer_html_path = os.path.join(temp_dir, "footer.html")
        cover_html_path = os.path.join(temp_dir, "cover.html")
        report_html_path = os.path.join(temp_dir, "report.html")

        subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                         '--header-html', header_html_path, '--footer-html', footer_html_path,
                         'cover', cover_html_path, report_html_path, pdfpath])
        return pdfpath