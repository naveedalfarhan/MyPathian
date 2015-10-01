import uuid
import pyodbc
from db.uow import UoW


def convert_timezone(timezone):
    if timezone == "Eastern Standard Time":
        return "US/Eastern"
    if timezone == "Central Standard Time":
        return "US/Central"


class AccountImporter:

    def __init__(self):
        self.conn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=PathianDBNet;integrated security=True")
        self.group_dict = {}
        self.ws_dict = {}
        self.account_dict = {}
        self.uow = UoW(None)
        pass

    def load_groups(self):
        groups = self.uow.groups.get_all()
        for group in groups:
            if "old_id" in group:
                self.group_dict[group["old_id"]] = group["id"]
        print("groups loaded")

    def load_weatherstations(self):
        weatherstations = self.uow.weather_stations.get_all(raw=True)
        for weatherstation in weatherstations:
            if "old_id" in weatherstation:
                self.ws_dict[weatherstation["old_id"]] = weatherstation["id"]
        print("weatherstations loaded")

    def import_accounts(self):
        self.uow.accounts.delete_all()
        cursor = self.conn.cursor()

        cursor.execute("""SELECT a.Id, a.Name, a.Num, a.GroupId, a.AccountTypeId, a.WeatherStationId, a.TimeZoneInfoId,
                        a.UsesUtilityBillImport, a.EquipmentId, a.UtilityCompanyId, aty.Name as TypeName
                        FROM Accounts a
                        INNER JOIN AccountTypes aty ON a.AccountTypeId = aty.Id""")

        accounts = []

        for row in cursor:
            new_id = str(uuid.uuid4())
            new_account = {"id": new_id, "name": row.Name, "num": row.Num, "old_account_type_id": row.AccountTypeId,
                           "weatherstation_id": self.ws_dict[row.WeatherStationId],
                           "old_weatherstation_id": row.WeatherStationId,
                           "uses_utility_bill_import": row.UsesUtilityBillImport, "old_id": row.Id,
                           "type": row.TypeName,
                           "timezone": convert_timezone(row.TimeZoneInfoId)}

            if row.GroupId is not None:
                new_account["old_group_id"] = row.GroupId
                if row.GroupId in self.group_dict:
                    new_account["group_id"] = self.group_dict[row.GroupId]

            if row.EquipmentId is not None:
                new_account["old_equipment_id"] = row.EquipmentId

            if row.UtilityCompanyId is not None:
                new_account["old_utility_company_id"] = row.UtilityCompanyId

            accounts.append(new_account)

            self.account_dict[row.Id] = new_id

        self.uow.accounts.insert_batch(accounts)
        print("imported accounts")


if __name__ == "__main__":
    importer = AccountImporter()
    importer.load_groups()
    importer.load_weatherstations()
    importer.import_accounts()