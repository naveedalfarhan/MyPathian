class Contact:
    def __init__(self, p=None):
        self.id = None
        self.first_name = None
        self.last_name = None
        self.full_name = None
        self.title = None
        self.email = None
        self.comments = None
        self.address = None
        self.city = None
        self.state = None
        self.zip = None
        self.group_id = None
        self.category_id = None

        if p is not None:
            if "id" in p:
                self.id = p["id"]
            if "first_name" in p:
                self.first_name = p["first_name"]
            if "last_name" in p:
                self.last_name = p["last_name"]
            if "first_name" in p and "last_name" in p:
                self.full_name = p["first_name"] + " " + p["last_name"]
            if "title" in p:
                self.title = p["title"]
            if "email" in p:
                self.email = p["email"]
            if "comments" in p:
                self.comments = p["comments"]
            if "address" in p:
                self.address = p["address"]
            if "city" in p:
                self.city = p["city"]
            if "state" in p:
                self.state = p["state"]
            if "zip" in p:
                self.zip = p["zip"]
            if "group_id" in p:
                self.group_id = p["group_id"]
            else:
                self.group_id=""
            if "category_id" in p:
                self.category_id = p["category_id"]
            else:
                self.category_id=""