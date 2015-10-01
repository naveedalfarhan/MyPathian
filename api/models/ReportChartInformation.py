class ReportChartInformation:
    def __init__(self, p=None):
        self.x_axis_label = None
        self.y_axis_label = None
        self.title = None
        self.data = None

        if p:
            self.__dict__.update(**p)