class SizeNormalization:
    def __init__(self, p=None):
        self.id = None
        self.effective_date = None
        self.value = None  # cost per unit of energy
        self.note = None
        self.account_id = None
        if p is not None:
            if "id" in p:
                self.id = p["id"]
            if "effective_date" in p:
                self.effective_date = p["effective_date"]
            if "value" in p:
                self.value = p["value"]
            if "note" in p:
                self.note = p["note"]
            if "account_id" in p:
                self.account_id = p["account_id"]