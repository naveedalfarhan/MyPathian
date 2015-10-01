class Eco:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.description = None
        self.memo = None
        self.comments = None
        self.project_id = None
        self.equipment_id = None
        self.reduction_goal = None
        self.reduction_units = None
        self.original_date = None
        self.completion_goal = None

        if p:
            if "id" in p:
                self.id = p["id"]
            if "name" in p:
                self.name = p["name"]
            if "description" in p:
                self.description = p["description"]
            if "memo" in p:
                self.memo = p["memo"]
            if "comments" in p:
                self.comments = p["comments"]
            if "project_id" in p:
                self.project_id = p["project_id"]
            if "equipment_id" in p:
                self.equipment_id = p["equipment_id"]
            if "reduction_goal" in p:
                self.reduction_goal = p["reduction_goal"]
            if "reduction_units" in p:
                self.reduction_units = p["reduction_units"]
            if "original_date" in p:
                self.original_date = p["original_date"]
            if "completion_goal" in p:
                self.completion_goal = p["completion_goal"]