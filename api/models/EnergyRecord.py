class EnergyRecord:
    def __init__(self, p=None):
        self.id = None
        self.account_id = None
        self.create_source = None
        self.readingdateutc = None
        self.hours_in_record = None
        self.local_day_of_week = None
        self.local_hour = None
        self.local_month = None
        self.local_year = None
        self.local_day_of_month = None
        self.price_normalization = None
        self.size_normalization = None
        self.type = None
        self.energy = {}
        self.weather = {}
        self.peak = None

        if p is not None:
            self.__dict__.update(**p)