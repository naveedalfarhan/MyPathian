class EquipmentParagraph:
    def __init__(self, data):
        self.description = None
        self.equipment_id = None
        self.id = None
        self.num = None
        self.paragraph_id = None
        self.sort_order = None
        self.title = None
        self.type = None
        self.category_id = None

        if data is not None:
            self.__dict__.update(**data)
