class TotalEnergyDataContainer:
    def __init__(self, p=None):
        self.title = None
        self.x_axis_label = None
        self.y_axis_label = None
        self.data = []

        if p:
            self.__dict__.update(**p)