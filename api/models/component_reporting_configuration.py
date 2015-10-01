class ComponentReportingConfiguration:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.report_year = None
        self.point_ids = []
        self.submitted_to = None

        if p:
            self.__dict__.update(**p)

        # convert all years to integers so it doesn't have to be done anywhere else
        if self.report_year:
            self.report_year = int(self.report_year)