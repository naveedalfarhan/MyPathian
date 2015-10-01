class ComponentTask:
    def __init__(self, p=None):
        self.id = None
        self.component_id = None
        self.num = None
        self.title = None
        self.description = None
        self.budget_year = None
        self.estimated_cost = None
        self.priority_id = None
        self.status_id = None
        self.type_id = None

        if p:
            self.__dict__.update(**p)