__author__ = 'badams'


class ComponentDifferenceDataContainer:
    def __init__(self, p=None):
        self.title = None
        self.x_axis_label = None
        self.y_axis_label = None
        self.consumption_data = None
        self.difference_data = None
        self.component_description = None

        if p:
            self.__dict__.update(**p)
