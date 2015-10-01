class UtilityCompany:
    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.address1 = None
        self.address2 = None
        self.city = None
        self.state = None
        self.zip = None
        self.contact_id = None

        if p is not None:
            if "id" in p:
                self.id = p["id"]
            if "name" in p:
                self.name = p["name"]
            if "address1" in p:
                self.address1 = p["address1"]
            if "address2" in p:
                self.address2 = p["address2"]
            if "city" in p:
                self.city = p["city"]
            if "state" in p:
                self.state = p["state"]
            if "zip" in p:
                self.zip = p["zip"]
            if "contact_id" in p:
                self.contact_id = p["contact_id"]
            else:
                self.contact_id = ""