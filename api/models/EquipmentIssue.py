class EquipmentIssue:
    def __init__(self, p=None):
        self.id = None
        self.title = None
        self.description = None
        self.issued_by_ids = []
        self.issued_to_ids = []
        self.group_id = None
        self.equipment_id = None
        self.open_date = None
        self.due_date = None
        self.priority_id = None
        self.status_id = None
        self.type_id = None

        if p:
            self.__dict__.update(**p)