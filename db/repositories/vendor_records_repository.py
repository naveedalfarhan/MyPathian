class VendorRecordsRepository:
    def __init__(self, uow):
        self.uow = uow

    def insert_vendor_records(self, records):
        self.uow.run(self.uow.tables.vendor_records.insert(records))

    def insert_fieldserver_points(self, points):
        if len(points) == 0:
            return

        self.uow.run(self.uow.tables.vendor_points.insert(points, conflict="replace"))

    def insert_invensys_points(self, points):
        if len(points) == 0:
            return

        self.uow.run(self.uow.tables.vendor_points.insert(points, conflict="replace"))

    def insert_johnson_points(self, points):
        if len(points) == 0:
            return

        self.uow.run(self.uow.tables.vendor_points.insert(points, conflict="replace"))
