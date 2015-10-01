class Contract:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.start_date = None
        self.end_date = None
        self.active = None
        self.purchase_order_number = None
        self.dollar_amount = None
        self.user_ids = []
        self.group_id = None

        if p is not None:
            if "id" in p:
                self.id = p["id"]
            if "name" in p:
                self.name = p["name"]
            if "start_date" in p:
                self.start_date = p["start_date"]
            if "end_date" in p:
                self.end_date = p["end_date"]
            if "active" in p:
                self.active = p["active"]
            if "group_name" in p:
                self.group_name = p["group_name"]
            if "purchase_order_number" in p:
                self.purchase_order_number = p["purchase_order_number"]
            if "dollar_amount" in p:
                self.dollar_amount = p["dollar_amount"]
            if "user_ids" in p:
                self.user_ids = p["user_ids"]
            if "group_id" in p:
                self.group_id = p["group_id"]