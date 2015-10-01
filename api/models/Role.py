class Role:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.created_date = None
        self.created_by = None
        self.last_modified_on = None
        self.last_modified_by = None
        self.permissions = []

        if p:
            self.__dict__.update(**p)