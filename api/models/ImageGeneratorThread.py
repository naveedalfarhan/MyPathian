from threading import Thread
from math import ceil, floor

import pygal

import os


__author__ = 'badams'


class ImageGeneratorThread(Thread):
    def __init__(self, config, series_data, directory, image_name):
        self.config = config
        # expects series data as a list of dictionaries in the form {"name":"", "data": [[x,y],[x,y]...]}
        self.series_data = series_data
        self.directory = directory
        self.image_name = image_name

        super(ImageGeneratorThread, self).__init__()  # super lets you avoid referring to the base class explicitly

    def run(self):
        self.config = self.config()

        # set the css
        self.config.css.append('inline: path { stroke-width:2 !important; } .guide { stroke-dasharray: none !important; stroke:#474747 !important; stroke-width:1; }')

        # generate an svg chart and return the graphic
        chart = pygal.XY(self.config)

        for entry in self.series_data:
            # if the list of data is empty, add an empty series to the chart
            if len(entry["data"]) > 0:
                # add entry to data in the proper form
                chart.add(entry["name"], [(xy[0], xy[1]) for xy in entry["data"]])
            else:
                # this prevents PyGal from throwing an exception while trying to interpolate
                chart.add(entry["name"], [(0,0)])

        # export the chart svg
        chart.render_to_file(os.path.join(self.directory, self.image_name))