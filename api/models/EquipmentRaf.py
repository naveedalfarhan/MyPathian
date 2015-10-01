class EquipmentRaf:
    def __init__(self, entries=None):
        self.id = None
        self.equipment_id = None
        self.name = None
        self.inlet_pressure = None
        self.discharge_pressure = None
        self.delta_p = None
        self.mixing_box_pressure = None

        if entries is not None:
            self.__dict__.update(**entries)