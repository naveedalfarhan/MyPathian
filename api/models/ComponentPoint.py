class ComponentPoint:
    def __init__(self, entries=None):
        self.id = None
        self.point_type = None
        self.component_point_num = None
        self.component_id = None
        self.description = []
        self.master_point = None
        self.code = None

        if entries is not None:
            self.__dict__.update(**entries)