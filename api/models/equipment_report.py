__author__ = 'badams'


class EquipmentReport():
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.report_year = None
        self.comparison_year = None
        self.syrx_num = None
        self.submitted_to = None
        self.report_type = None
        self.equipment_id = None
        self.syrx_nums = None
        self.start_month = None
        self.end_month = None

        if p:
            self.__dict__.update(**p)

        # convert all years and months to integers so it doesn't have to be done anywhere else
        if self.report_year:
            self.report_year = int(self.report_year)
        if self.comparison_year:
            self.comparison_year = int(self.comparison_year)
        if self.start_month:
            self.start_month = int(self.start_month)
        if self.end_month:
            self.end_month = int(self.end_month)