import math
import datetime
from db.uow import UoW
import pytz


class EnergyRecordCompiler:
    def __init__(self):
        self.uow = UoW(None)

    def compile_energy_records(self):

        count = 0
        data_list = []

        # compile electric records
        for comparison_type in ["temp", "dewpt", "enthalpy"]:
            data = self.uow.compiled_energy_records.get_compiled_energy_records("electric", comparison_type)

            for entry in data:
                count += 1
                if entry['group']:
                    data_list.append(
                        {"account_id": entry["group"]["account_id"],
                             "comparison_type": comparison_type,
                         'comparison_value': entry["group"]["comparison_value"],
                         "year": entry["group"]["year"], "month": entry["group"]["month"],
                         "sum_btu": entry["reduction"]["btu"],
                         'sum_kvar': entry['reduction']['kvar'],
                         'kva': math.sqrt(math.pow(entry['reduction']['kwh'], 2) + math.pow(entry['reduction']['kvar'], 2)),
                         'pf': entry['reduction']['kwh'] / math.sqrt(
                             math.pow(entry['reduction']['kwh'], 2) + math.pow(entry['reduction']['kvar'], 2)),
                         "sum_size_normalization": entry["reduction"]["size_normalization"],
                         "sum_price_normalization": entry["reduction"]["price_normalization"],
                         "sum_hours_in_record": entry["reduction"]["hrs"],
                         'peak': entry['group']['peak']})
                    if count % 1000 == 0:
                        self.uow.compiled_energy_records.insert_compiled_energy_records(data_list)
                        data_list = []
                        print "Compiled " + str(count) + " records."

        # compile gas records
        for comparison_type in ["temp", "dewpt", "enthalpy"]:
            data = self.uow.compiled_energy_records.get_compiled_energy_records("gas", comparison_type)

            for entry in data:
                count += 1
                if entry['group']:
                    data_list.append(
                        {"account_id": entry['group']['account_id'],
                             'comparison_type': comparison_type,
                         'comparison_value': entry['group']['comparison_value'],
                         'year': entry['group']['year'], 'month': entry['group']['month'],
                         'sum_btu': entry['reduction']['btu'],
                         "sum_size_normalization": entry["reduction"]["size_normalization"],
                         "sum_price_normalization": entry["reduction"]["price_normalization"],
                         "sum_hours_in_record": entry["reduction"]["hrs"],
                         'peak': entry['group']['peak']})
                if count % 1000 == 0:
                    self.uow.compiled_energy_records.insert_compiled_energy_records(data_list)
                    data_list = []
                    print "Compiled " + str(count) + " records."

        self.uow.compiled_energy_records.insert_compiled_energy_records(data_list)
        print "Compiled " + str(count) + " records."

    def compile_component_point_records(self):

        count = 0
        data_list = []

        for comparison_type in ["temp", "dewpt", "enthalpy"]:
            data = self.uow.compiled_energy_records.get_compiled_component_point_records(comparison_type)

            for entry in data:
                count += 1
                equipment_point = self.uow.equipment.get_equipment_point_by_syrx_num(entry["group"]["syrx_num"])
                component_point = self.uow.component_points.get_by_component_point_id(equipment_point["component_point_id"])
                data_list.append(
                    {"syrx_num": entry["group"]["syrx_num"],
                     "comparison_type": comparison_type,
                     'comparison_value': entry["group"]["comparison_value"],
                     "year": entry["group"]["year"], "month": entry["group"]["month"],
                     "sum_value": entry["reduction"]["value"],
                     "sum_hours_in_record": entry["reduction"]["hrs"],
                     'peak': entry['group']['peak'],
                     "point_num": component_point["component_point_num"]})

                if count % 1000 == 0:
                    self.uow.compiled_energy_records.insert_compiled_equipment_point_records(data_list)
                    data_list = []
                    print "Compiled " + str(count) + " records."

        self.uow.compiled_energy_records.insert_compiled_equipment_point_records(data_list)
        print "Compiled " + str(count) + " records."

    def compile_component_point_records_by_year_span(self, syrx_num, start_date, end_date):
        current_date = pytz.utc.localize(datetime.datetime.utcnow())
        equipment_point = self.uow.equipment.get_equipment_point_by_syrx_num(syrx_num)
        component_point = self.uow.component_points.get_by_component_point_id(equipment_point["component_point_id"])

        count = 0
        data_list = []

        for comparison_type in ["temp", "dewpt", "enthalpy"]:
            data = self.uow.compiled_energy_records.get_compiled_component_point_records(comparison_type, syrx_num,
                                                                                         start_date, end_date)

            for entry in data:
                count += 1
                data_list.append(
                    {"syrx_num": entry["group"]["syrx_num"],
                     "comparison_type": comparison_type,
                     'comparison_value': entry["group"]["comparison_value"],
                     "year": entry["group"]["year"], "month": entry["group"]["month"],
                     "sum_value": entry["reduction"]["value"],
                     "sum_hours_in_record": entry["reduction"]["hrs"],
                     'peak': entry['group']['peak'],
                     "created_on:": current_date,
                     "point_num":component_point["component_point_num"]})

                if count % 1000 == 0:
                    self.uow.compiled_energy_records.insert_compiled_equipment_point_records(data_list)
                    data_list = []
                    print "Compiled " + str(count) + " records."

        self.uow.compiled_energy_records.insert_compiled_equipment_point_records(data_list)
        print "Compiled " + str(count) + " records."

    @classmethod
    def get_grouping_for_type(cls, comparison_type):
        if comparison_type == "temp":
            grouping = lambda record: {'account_id': record['account_id'],
                                       'year': record['local_year'],
                                       'comparison_value': record['weather']['temp'],
                                       'month': record['local_month'],
                                       'type': record['type'],
                                       'peak': record['peak']}
        elif comparison_type == "dewpt":
            grouping = lambda record: {'account_id': record['account_id'],
                                       'year': record['local_year'],
                                       'comparison_value': record['weather']['dewpt'],
                                       'month': record['local_month'],
                                       'type': record['type'],
                                       'peak': record['peak']}
        elif comparison_type == "enthalpy":
            grouping = lambda record: {'account_id': record['account_id'],
                                       'year': record['local_year'],
                                       'comparison_value': record['weather']['enthalpy'],
                                       'month': record['local_month'],
                                       'type': record['type'],
                                       'peak': record['peak']}
        return grouping

    def get_compiled_electric_records(self, account_id, start_year, end_year, comparison_type):
        data = self.uow.compiled_energy_records.get_compiled_energy_records("electric",
                                                                            comparison_type,
                                                                            account_id=account_id,
                                                                            start_year=start_year,
                                                                            end_year=end_year)

        mapping = lambda record: {
            "account_id": record["group"]["account_id"],
            "comparison_type": comparison_type,
            'comparison_value': record["group"]["comparison_value"],
            "year": record["group"]["year"],
            "month": record["group"]["month"],
            "sum_btu": record["reduction"]["btu"],
            "sum_kwh": record["reduction"]["kwh"],
            'sum_kvar': record['reduction']['kvar'],
            'kva': math.sqrt(math.pow(record['reduction']['kwh'], 2) + math.pow(record['reduction']['kvar'], 2)),
            'pf': record['reduction']['kwh'] /
                  math.sqrt(math.pow(record['reduction']['kwh'], 2) + math.pow(record['reduction']['kvar'], 2)),
            "sum_size_normalization": record["reduction"]["size_normalization"],
            "sum_price_normalization": record["reduction"]["price_normalization"],
            "sum_hours_in_record": record["reduction"]["hrs"],
            'peak': record['group']['peak']
        }

        data = map(mapping, data)
        return data

    def get_compiled_nonelectric_records(self, account_id, start_year, end_year, comparison_type):
        data = self.uow.compiled_energy_records.get_compiled_energy_records("gas",
                                                                            comparison_type,
                                                                            account_id=account_id,
                                                                            start_year=start_year,
                                                                            end_year=end_year)

        mapping = lambda record: {
            "account_id": record["group"]["account_id"],
            "comparison_type": comparison_type,
            'comparison_value': record["group"]["comparison_value"],
            "year": record["group"]["year"],
            "month": record["group"]["month"],
            "sum_btu": record["reduction"]["btu"],
            "sum_size_normalization": record["reduction"]["size_normalization"],
            "sum_price_normalization": record["reduction"]["price_normalization"],
            "sum_hours_in_record": record["reduction"]["hrs"],
            'peak': record['group']['peak']
        }

        data = map(mapping, data)
        return data

    def compile_energy_records_by_year_span(self, start_year, end_year, account_id):

        count = 0

        account_type = self.uow.accounts.get_by_id(account_id).type

        for comparison_type in ["temp", "dewpt", "enthalpy"]:
            if account_type == "electric":
                data = self.get_compiled_electric_records(account_id, start_year, end_year, comparison_type)
            else:
                data = self.get_compiled_nonelectric_records(account_id, start_year, end_year, comparison_type)

            data_list = []

            for entry in data:
                count += 1
                data_list.append(entry)

                if count % 1000 == 999:
                    self.uow.compiled_energy_records.insert_compiled_energy_records(data_list)
                    data_list = []
                    print "Compiled " + str(count) + " records."
            if len(data_list) > 0:
                self.uow.compiled_energy_records.insert_compiled_energy_records(data_list)
                data_list = []
                print "Compiled " + str(count) + " records."


    def get_compiled_electric_records_for_date_span(self, account_id, start_date, end_date, comparison_type):
        data = self.uow.compiled_energy_records.get_compiled_energy_records("electric",
                                                                            comparison_type,
                                                                            account_id=account_id,
                                                                            start_date=start_date,
                                                                            end_date=end_date)

        mapping = lambda record: {
            "account_id": record["group"]["account_id"],
            "comparison_type": comparison_type,
            'comparison_value': record["group"]["comparison_value"],
            "year": record["group"]["year"],
            "month": record["group"]["month"],
            "sum_btu": record["reduction"]["btu"],
            "sum_kwh": record["reduction"]["kwh"],
            'sum_kvar': record['reduction']['kvar'],
            'kva': math.sqrt(math.pow(record['reduction']['kwh'], 2) + math.pow(record['reduction']['kvar'], 2)),
            'pf': record['reduction']['kwh'] /
                  math.sqrt(math.pow(record['reduction']['kwh'], 2) + math.pow(record['reduction']['kvar'], 2)),
            "sum_size_normalization": record["reduction"]["size_normalization"],
            "sum_price_normalization": record["reduction"]["price_normalization"],
            "sum_hours_in_record": record["reduction"]["hrs"],
            'peak': record['group']['peak']
        }

        data = map(mapping, data)
        return data

    def get_compiled_nonelectric_records_for_date_span(self, account_id, start_date, end_date, comparison_type):
        data = self.uow.compiled_energy_records.get_compiled_energy_records("gas",
                                                                            comparison_type,
                                                                            account_id=account_id,
                                                                            start_date=start_date,
                                                                            end_date=end_date)

        mapping = lambda record: {
            "account_id": record["group"]["account_id"],
            "comparison_type": comparison_type,
            'comparison_value': record["group"]["comparison_value"],
            "year": record["group"]["year"],
            "month": record["group"]["month"],
            "sum_btu": record["reduction"]["btu"],
            "sum_size_normalization": record["reduction"]["size_normalization"],
            "sum_price_normalization": record["reduction"]["price_normalization"],
            "sum_hours_in_record": record["reduction"]["hrs"],
            'peak': record['group']['peak']
        }

        data = map(mapping, data)
        return data

    def compile_energy_records_by_date_span(self, start_date, end_date, account_id):

        count = 0

        account_type = self.uow.accounts.get_by_id(account_id).type.lower()

        # remove existing entries in this datetime span
        self.uow.compiled_energy_records.delete_compiled_records(account_id, start_date, end_date)

        for comparison_type in ["temp", "dewpt", "enthalpy"]:
            if account_type == "electric":
                data = self.get_compiled_electric_records_for_date_span(account_id, start_date, end_date, comparison_type)
            else:
                data = self.get_compiled_nonelectric_records_for_date_span(account_id, start_date, end_date, comparison_type)

            data_list = []

            for entry in data:
                count += 1
                data_list.append(entry)

                if count % 200 == 199:
                    self.uow.compiled_energy_records.insert_compiled_energy_records(data_list)
                    data_list = []
                    print "Compiled " + str(count) + " records."
            if len(data_list) > 0:
                self.uow.compiled_energy_records.insert_compiled_energy_records(data_list)
                data_list = []
                print "Compiled " + str(count) + " records."


if __name__ == "__main__":
    compiler = EnergyRecordCompiler()
    #compiler.compile_energy_records()
    compiler.compile_component_point_records()
