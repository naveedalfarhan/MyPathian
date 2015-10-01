import os

from pygal import Config
from pygal.style import LightStyle

import server


__author__ = 'badams'


class ChartConfig(Config):
    show_dots = False
    show_legend = True
    fill = False
    width = 350
    height = 350
    explicit_size = True
    interpolate = 'cubic'

    # style
    style = LightStyle
    style.plot_background = 'rgba(255,255,255,1)'

    legend_at_bottom = True
    js = ()
    no_data_text = ''
    print_values = False
    print_zeroes = False
    disable_xml_declaration = True
    no_prefix = True
    label_font_size = 14
    major_label_font_size = 14
    show_x_guides = True