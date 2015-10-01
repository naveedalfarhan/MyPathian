class Task:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.description = None
        self.budget_year = None
        self.estimated_cost = None
        self.priority_id = None
        self.status_id = None
        self.type_id = None
        self.accepted_date = None
        self.start_date = None
        self.completed_date = None
        self.assigned_to_id = None
        self.group_id = None
        self.equipment_id = None

        if p:
            self.__dict__.update(**p)