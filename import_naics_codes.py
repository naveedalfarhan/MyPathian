import pyodbc
from db.uow import UoW


class NaicsImporter:
    def __init__(self):
        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=PathianDBNet;integrated security=True")
        self.uow = UoW(None)


    def import_codes(self):
        self.uow.naics.delete_all()
        cursor = self.conn.cursor()

        cursor.execute("SELECT Code, Description, ParentCode FROM NaicsCodes")

        codes = []

        for row in cursor:
            new_code = {"code": row.Code, "description": row.Description, "parent_code": row.ParentCode,
                        "name": row.Code + " - " + row.Description, "numeric_code": int(row.Code)}

            codes.append(new_code)

        self.uow.naics.insert_batch(codes)
        print "imported NAICS codes"


if __name__ == "__main__":
    importer = NaicsImporter()
    importer.import_codes()