class ActionItemType:
    def __init__(self, p=None):
        self.id = None
        self.name = None

        if p is not None:
            if "id" in p:
                self.id = p["id"]
            if "name" in p:
                self.name = p["name"]