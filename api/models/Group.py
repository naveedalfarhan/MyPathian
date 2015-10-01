class Group:
    def __init__(self, entries=None):
        self.id = None
        self.name = None
        self.childIds = []
        self.parentIds = []
        self.weatherstation_id = None

        # contact info
        self.email = None
        self.address = None
        self.city = None
        self.state = None
        self.zip = None
        self.first_name = None
        self.last_name = None
        self.job_title = None

        self.naics_code = None
        self.sic_code = None

        if entries is not None:
            self.__dict__.update(**entries)