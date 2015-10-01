class ResetSchedule:
    def __init__(self, values):
        self.id = None
        self.name = None
        self.header1 = None
        self.header2 = None
        self.row1val1 = None
        self.row1val2 = None
        self.row2val1 = None
        self.row2val2 = None

        if values:
            self.__dict__.update(**values)
