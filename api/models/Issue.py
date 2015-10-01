class Issue:
    def __init__(self, p=None):
        self.id = None
        self.name = None
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

        if p is not None:
            if "id" in p:
                self.id = p["id"]
            if "name" in p:
                self.name = p["name"]
            if "description" in p:
                self.description = p["description"]
            if "issued_by_ids" in p:
                self.issued_by_ids = p["issued_by_ids"]
            if "issued_to_ids" in p:
                self.issued_to_ids = p["issued_to_ids"]
            if "group_id" in p:
                self.group_id = p["group_id"]
            if "equipment_id" in p:
                self.equipment_id = p["equipment_id"]
            if "open_date" in p:
                self.open_date = p["open_date"]
            if "due_date" in p:
                self.due_date = p["due_date"]
            if "priority_id" in p:
                self.priority_id = p["priority_id"]
            if "status_id" in p:
                self.status_id = p["status_id"]
            if "type_id" in p:
                self.type_id = p["type_id"]