__author__ = 'badams'


class ComponentReportingDifferenceConfiguration:
    def __init__(self, p=None):
        self.id = None
        self.report_year = None
        self.benchmark_year = None
        self.start_month = None
        self.end_month = None
        self.component_ids = None
        self.submitted_to = None
        self.selected_component = None

        if p:
            self.__dict__.update(**p)

        # make sure the report and benchmark years are integer
        if self.report_year:
            self.report_year = int(self.report_year)
        if self.benchmark_year:
            self.benchmark_year = int(self.benchmark_year)