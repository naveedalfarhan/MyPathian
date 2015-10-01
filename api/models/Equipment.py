class Equipment:
    def __init__(self, entries):
        self.id = None
        self.group_id = None
        self.name = None
        self.description = None
        self.department = None
        self.model = None
        self.manufacturer = None
        self.serial = None
        self.install_date = None
        self.demo_date = None
        self.location = None
        self.subcomponent_ids = None

        if entries is not None:
            self.__dict__.update(**entries)