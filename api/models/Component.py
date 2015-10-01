class Component:
    def __init__(self, p=None):
        self.id = None
        self.num = None
        self.description = None
        self.structure_parent_id = None
        self.structure_child_ids = []
        self.master_point = None
        if p is not None:
            self.__dict__.update(**p)