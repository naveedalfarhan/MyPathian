class Project:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.group_id = None
        self.address = None
        self.customer_project_id = None
        self.architect_project_id = None
        self.start_date = None
        self.complete_date = None
        self.estimated_cost = None
        self.owner_id = None
        self.comm_authority_id = None
        self.engineer_id = None

        if p:
            if "id" in p:
                self.id = p["id"]
            if "name" in p:
                self.name = p["name"]
            if "group_id" in p:
                self.group_id = p["group_id"]
            if "address" in p:
                self.address = p["address"]
            if "customer_project_id" in p:
                self.customer_project_id = p["customer_project_id"]
            if "architect_project_id" in p:
                self.architect_project_id = p["architect_project_id"]
            if "start_date" in p:
                self.start_date = p["start_date"]
            if "complete_date" in p:
                self.complete_date = p["complete_date"]
            if "estimated_cost" in p:
                self.estimated_cost = p["estimated_cost"]
            if "owner_id" in p:
                self.owner_id = p["owner_id"]
            if "comm_authority_id" in p:
                self.comm_authority_id = p["comm_authority_id"]
            if "engineer_id" in p:
                self.engineer_id = p["engineer_id"]