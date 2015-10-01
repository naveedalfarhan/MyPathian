class Account:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.num = None
        self.timezone = None
        self.group_id = None
        self.weatherstation_id = None
        self.type = None
        self.deviation_threshold = None
        self.disable_alarm = None

        if p:
            self.__dict__.update(**p)
