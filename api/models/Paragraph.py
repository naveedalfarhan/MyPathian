class Paragraph:
    def __init__(self, p=None):
        self.id = None
        self.component_id = None
        self.title = None
        self.description = None
        self.type = None
        self.category_id = None
        self.num = None

        if p:
            self.__dict__.update(**p)