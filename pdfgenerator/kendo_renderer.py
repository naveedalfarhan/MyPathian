from copy import deepcopy, copy
import json
import shutil
import tempfile
from flask.json import jsonify
import os
import pkg_resources
from selenium import webdriver
from selenium.webdriver.common.utils import free_port


class KendoRenderer:
    def __init__(self, javascript=""):
        self.javascript = javascript
        self.width = 600
        self.height = 400
        self.temp_dir = None

    def set_dimensions(self, width=600, height=400):
        self.width = width
        self.height = height

    def set_chart_options(self, title, x_axis_label, y_axis_label, series_data):
        config = {
            "transitions": False,
            "title": {"text": title},
            "legend": {
                "visible": True,
                "position": "top"
            },
            "chartArea": {"background": ""},
            "xAxis": {
                "labels": {"format": '{0}'},
                "title": {"text": x_axis_label}
            },
            "yAxis": {
                "labels": {"format": '{0}'},
                "title": {"text": y_axis_label}
            },
            "series": series_data,
            "seriesDefaults": {
                "type": 'scatterLine',
                "width": 3,
                "style": 'smooth',
                "markers": {
                    "size": 1
                }
            }
        }
        self.javascript = "$(function(){$('#chart').kendoChart(" + \
                          json.dumps(config) + \
                          ");});"

    def __create_temp_files(self):
        temp_dir = tempfile.mkdtemp()

        files_to_copy = [
            pkg_resources.resource_filename("pdfgenerator.kendo_renderer", "kendo_chart.html"),
            pkg_resources.resource_filename("pdfgenerator.kendo_renderer", "jquery-1.10.2.min.js"),
            pkg_resources.resource_filename("pdfgenerator.kendo_renderer", "kendo.all.min.js"),
            pkg_resources.resource_filename("pdfgenerator.kendo_renderer", "kendo.common.min.css"),
            pkg_resources.resource_filename("pdfgenerator.kendo_renderer", "kendo.default.min.css")
        ]

        for file_path in files_to_copy:
            shutil.copy(file_path, temp_dir)

        data_js = os.path.join(temp_dir, "data.js")
        fo = open(data_js, "w+")
        fo.write(self.javascript)
        fo.close()

        return temp_dir

    def __create_image(self):
        driver = webdriver.PhantomJS()

        # there seems to be a 4 pixel border added to the image
        driver.set_window_size(self.width - 8, self.height - 8)

        driver.get(os.path.join(self.temp_dir, "kendo_chart.html"))
        driver.save_screenshot(os.path.join(self.temp_dir, "image.png"))
        driver.quit()

        image_file = tempfile.TemporaryFile()
        f = open(os.path.join(self.temp_dir, "image.png"), "rb")
        buf = f.read(1024)
        while len(buf):
            image_file.write(buf)
            buf = f.read(1024)
        f.close()
        image_file.seek(0)

        return image_file

    def __delete_temp_dir(self):
        # shutil.rmtree(self.temp_dir)
        pass


    def get_image_file_handle(self):
        self.temp_dir = self.__create_temp_files()
        image_file_handle = self.__create_image()
        self.__delete_temp_dir()

        return image_file_handle


