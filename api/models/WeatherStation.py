class WeatherStation:
    def __init__(self, entries=None):
        self.id = None
        self.name = None
        self.usaf = None
        self.wban = None
        self.years = []

        if entries is not None:
            self.__dict__.update(**entries)
