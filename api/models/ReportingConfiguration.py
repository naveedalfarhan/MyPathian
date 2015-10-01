class ReportingConfiguration:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.report_year = None
        self.benchmark_year = None
        self.start_month = None
        self.end_month = None
        self.comparison_type = None
        self.demand_type = None
        self.account_type = None
        self.entity_ids = []
        self.electric_units = None
        self.gas_units = None
        self.btu_units = None
        self.submitted_to = None

        if p:
            self.__dict__.update(**p)

        # convert all years to integers so it doesn't have to be done anywhere else
        if self.report_year:
            self.report_year = int(self.report_year)

        if self.benchmark_year:
            self.benchmark_year = int(self.benchmark_year)