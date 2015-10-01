class NaicsReportingConfiguration:
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
        self.naics_codes = []
        self.report_type = None
        self.electric_units = None
        self.gas_units = None
        self.btu_units = None

        if p:
            self.__dict__.update(**p)