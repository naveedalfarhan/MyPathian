class TotalEnergyData:
    def __init__(self, p=None):
        self.entity_name = None
        self.account_name = None
        self.year = None
        self.reported_consumption = None
        self.benchmark_consumption = None
        self.diff = None
        self.benchmark_diff = None
        self.cost_reduction = None
        self.difference = None
        self.calculated_at = None

        if p:
            self.__dict__.update(**p)