from datetime import datetime
from itertools import groupby
import json
import subprocess
import tempfile
import shutil
import os
import pkg_resources

report_templates_package = "report_templates"


def create_temp_dir(report_options, file_paths_to_copy):
    temp_dir = tempfile.mkdtemp()

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


def generate_paragraph_report(report_config, submitted_to, submitted_by):
    reporting_equipments = []

    for equipment in report_config["equipments"]:
        # all this query does is it takes the list of paragraphs and puts them into dictionaries keyed
        # first by paragraph type, then by component num, then by category.
        paragraphs = dict(
            (paragraph_type, dict(
                (component_num, dict(
                    (category_name, sorted(category_paragraph_list, key=lambda x: x["sort_order"]))
                    for category_name, category_paragraph_list
                    in groupby(sorted(component_paragraph_list, key=lambda x: x["category_name"]), lambda x: x["category_name"])))
                for component_num, component_paragraph_list
                in groupby(sorted(type_paragraph_list, key=lambda x: x["component_num"]), lambda x: x["component_num"])))
            for paragraph_type, type_paragraph_list
            in groupby(sorted(equipment["paragraphs"], key=lambda x: x["type"]), lambda x: x["type"]))

        reporting_equipments.append({
            "equipment": equipment["equipment"],
            "paragraphs": paragraphs
        })

    report_options = {
        "equipments": reporting_equipments,
        "reportdate": str(datetime.now().strftime("%m/%d/%Y")),
        "submittedto": submitted_to,
        "submittedby": submitted_by,
        "reportname": "Syrx"
    }

    # this is a list of all of the static files necessary to generate the pdf
    package_subfile = "paragraph"
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

    temp_dir = create_temp_dir(report_options, file_paths_to_copy)
    pdfname = "paragraph_report-" + datetime.now().strftime("%Y-%m-%d %H %M %S") + ".pdf"
    pdfpath = os.path.join(temp_dir, pdfname)
    header_html_path = os.path.join(temp_dir, "header.html")
    footer_html_path = os.path.join(temp_dir, "footer.html")
    cover_html_path = os.path.join(temp_dir, "cover.html")
    report_html_path = os.path.join(temp_dir, "report.html")

    subprocess.call(['wkhtmltopdf', '-B', '2cm', '-L', '2cm', '-T', '2cm', '-R', '2cm',
                     '--header-html', header_html_path, '--footer-html', footer_html_path,
                     'cover', cover_html_path, report_html_path, pdfpath])

    return pdfpath

if __name__ == "__main__":
    components = [
        {
            "num": "23",
            "description": "HEATING, VENTILATING, AND AIR-CONDITIONING (HVAC)",
            "paragraphs": ["p1", "p2", "p3"],
            "components": [
                {
                    "num": "23 70",
                    "description": "CENTRAL HVAC EQUIPMENT",
                    "paragraphs": ["p1", "p2", "p3"],
                    "components": [
                        {
                            "num": "23 73 23",
                            "description": "Custom Indoor Central-Station Air-Handling Units",
                            "paragraphs": ["p1", "p2", "p3"],
                            "components": []
                        }
                    ]
                }
            ]
        }
    ]
    print(generate_paragraph_report(components))