__author__ = 'badams'


class ComponentReportingComparisonConfiguration:
    def __init__(self, p):
        self.id = None
        self.comparison_year = None
        self.start_month = None
        self.end_month = None
        self.historical_mode = None
        self.historical_years = []
        self.component_ids = []
        self.submitted_by = None
        self.unit = None

        if p:
            self.__dict__.update(**p)

        # make sure each year is an integer
        self.historical_years = [int(year) for year in self.historical_years]