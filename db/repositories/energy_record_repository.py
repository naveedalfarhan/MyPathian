import datetime
import pytz
import rethinkdb as r
from itertools import groupby


class EnergyRecordRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.energyrecords

    def insert_many(self, energy_records):
        self.uow.run(self.table.insert(energy_records))

    def delete_range(self, account_id, start_date, end_date):
        self.uow.run(self.table
                     .between([account_id, start_date], [account_id, end_date],
                              right_bound="closed", index="account_utc_date")
                     .delete(durability="hard"))

        compiled_index_values = []

        compiled_index_values.append([account_id, start_date.year, start_date.month])

        date = datetime.date(start_date.year, start_date.month, 1)
        first_day_of_end_date_month = datetime.date(end_date.year, end_date.month, 1)
        while date < first_day_of_end_date_month:
            month = date.month + 1
            year = date.year + (month - 1) / 12
            month = (month - 1) % 12 + 1
            date = datetime.date(year, month, 1)
            compiled_index_values.append([account_id, year, month])

        self.uow.run(self.uow.tables.compiled_energy_records
                     .get_all(*compiled_index_values, index="account_year_month")
                     .delete(durability="hard"))

    def insert_equipment_point_records(self, records):
        self.uow.run(self.uow.tables.equipment_point_records.insert(records))

        records_by_syrx_num = dict((k, list(v)) for k, v in groupby(records, lambda x: x["syrx_num"]))
        syrx_nums = records_by_syrx_num.keys()

        equipment_points = []
        if len(syrx_nums) > 0:
            equipment_points = self.uow.run_list(self.uow.tables.equipment_points.get_all(*syrx_nums, index="syrx_num"))

        equipment_points_to_update = []
        for point in equipment_points:
            min_date = min([record["date"] for record in records_by_syrx_num[point["syrx_num"]]])
            max_date = max([record["date"] for record in records_by_syrx_num[point["syrx_num"]]])

            if "min_date" in point:
                min_date = min([min_date, point["min_date"]])
            if "min_date" not in point or min_date < point["min_date"]:
                point["min_date"] = min_date
                equipment_points_to_update.append(point)

            if "max_date" in point:
                max_date = max([max_date, point["max_date"]])
            if "max_date" not in point or max_date > point["max_date"]:
                point["max_date"] = max_date
                equipment_points_to_update.append(point)

        self.uow.run(self.uow.tables.equipment_points.insert(equipment_points_to_update, conflict="update"))


    def get_equipment_point_records_by_syrx_date(self, keys):
        # keys of the form [[syrx_num1, date1], [syrx_num2, date2], ...]
        if len(keys) == 0:
            return []

        return self.uow.run_list(self.uow.tables.equipment_point_records.get_all(*keys, index="syrx_num_date"))


    def delete_equipment_point_range(self, syrx_num, start_date, end_date):
        self.uow.run(self.uow.tables.equipment_point_records
                     .between([syrx_num, start_date], [syrx_num, end_date],
                              right_bound="closed", index="syrx_num_date")
                     .delete(durability="hard"))

    def delete_equipment_point_records(self, keys):
        # keys of the form [[syrx_num1, date1], [syrx_num2, date2], ...]
        if len(keys) == 0:
            return
        self.uow.run(self.uow.tables.equipment_point_records.get_all(*keys, index="syrx_num_date").delete())

    def get_peak_records(self, account_year_pairs):
        return self.uow.run_list(self.table.get_all(*account_year_pairs, index='peak_report')
                                 .map(lambda record: {'account_id': record['account_id'],
                                                      'readingdateutc': record['readingdateutc'],
                                                      'demand': record['energy']['demand'],
                                                      'weather': record['weather']})
                                 .order_by(r.desc('demand')).limit(50))

    def get_all_for_account_date(self, account_id, year, month, day):
        return self.uow.run_list(self.table.get_all([account_id, year, month, day], index='account_date'))


    def update_price_norms(self, price_norm):
        # get the energy records in between this price normalization and the next, if there is a next
        all_prices = self.uow.run_list(self.uow.tables.pricenormalizations
                                       .get_all(price_norm.account_id, index='account_id')
                                       .order_by('effective_date'))

        next_price = None
        use_next = False

        # get the next price normalization
        for price in all_prices:
            if use_next:
                next_price = price
            if price['id'] == price_norm.id:
                use_next = True

        # next_price = None, then go until the current date
        if not next_price:
            end_date = pytz.utc.localize(datetime.datetime.utcnow())
        else:
            end_date = next_price['effective_date']

        # update the independent energy records for the account in between the two datetimes
        self.uow.run(self.table.get_all(price_norm.account_id, index='account_id')
                     .filter(lambda record: record['readingdateutc'].date().during(price_norm.effective_date, end_date))
                     .update({'price_normalization': price_norm.value}))

        return end_date

    def update_price_normalizations_from_delete(self, price_norm):
        # get all price normalizations for account
        all_prices = self.uow.run_list(self.uow.tables.pricenormalizations
                                       .get_all(price_norm.account_id, index='account_id')
                                       .order_by('effective_date'))

        prev_price = None
        use_next = False
        end_date = None
        # get the previous price normalization
        for price in all_prices:
            if use_next:
                end_date = price['effective_date']
                break
            if price['effective_date'] == price_norm.effective_date:
                use_next = True
            else:
                prev_price = price

        # make sure the user hasn't deleted the first price normalization
        if not prev_price:
            raise Exception("The earliest price normalization cannot be deleted.")

        if not end_date:
            # last price normalization was deleted, so we need to go until the current date
            end_date = pytz.utc.localize(datetime.datetime.utcnow())

        # update the independent energy records for the account in between the two datetimes
        self.uow.run(self.table.get_all(price_norm.account_id, index='account_id')
                     .filter(lambda record: record['readingdateutc'].date().during(price_norm.effective_date, end_date))
                     .update({'price_normalization': prev_price['value']}))

        # return end_date
        return end_date

    def update_size_norms(self, size_norm):
        # get the energy records in between this size normalization and the next, if there is a next
        all_sizes = self.uow.run_list(self.uow.tables.sizenormalizations
                                      .get_all(size_norm.account_id, index='account_id')
                                      .order_by('effective_date'))

        next_size = None
        use_next = False

        # get the next size normalization
        for size in all_sizes:
            if use_next:
                next_size = size
            if size['id'] == size_norm.id:
                use_next = True

        # next_size = None, then go until the current date
        if not next_size:
            end_date = pytz.utc.localize(datetime.datetime.utcnow())
        else:
            end_date = next_size['effective_date']

        # update the independent energy records for the account in between the two datetimes
        self.uow.run(self.table.get_all(size_norm.account_id, index='account_id')
                     .filter(lambda record: record['readingdateutc'].date().during(size_norm.effective_date, end_date))
                     .update({'size_normalization': size_norm.value}))

        return end_date

    def update_size_normalizations_from_delete(self, size_norm):
        # get all size normalizations for account
        all_sizes = self.uow.run_list(self.uow.tables.sizenormalizations
                                      .get_all(size_norm.account_id, index='account_id')
                                      .order_by('effective_date'))

        prev_size = None
        use_next = False
        end_date = None
        # get the previous size normalization
        for size in all_sizes:
            if use_next:
                end_date = size['effective_date']
                break
            if size['effective_date'] == size_norm.effective_date:
                use_next = True
            else:
                prev_size = size

        # make sure they don't delete the earliest size normalization
        if not prev_size:
            raise Exception("The earliest size normalization cannot be deleted.")

        if not end_date:
            # last size normalization was deleted, so we need to go until the current date
            end_date = pytz.utc.localize(datetime.datetime.utcnow())

        # update the independent energy records for the account in between the two datetimes
        self.uow.run(self.table.get_all(size_norm.account_id, index='account_id')
                     .filter(lambda record: record['readingdateutc'].date().during(size_norm.effective_date, end_date))
                     .update({'size_normalization': prev_size['value']}))

        # return end_date
        return end_date

    @staticmethod
    def get_equipment_point_record(date, syrx_num, value, weather, created_on):
        equipment_point_record = {
            "created_on": created_on,
            "date": date,
            "hours_in_record": 0.25,
            "local_day_of_month": date.day,
            "local_day_of_week": date.weekday(),
            "local_hour": date.hour,
            "local_month": date.month,
            "local_year": date.year,
            "syrx_num": syrx_num,
            "value": value,
            "weather": weather
        }

        if 13 <= date.hour < 18 and 6 <= date.month <= 8 and 0 <= date.weekday() <= 4:
            equipment_point_record["peak"] = 'peak'
        else:
            equipment_point_record["peak"] = 'offpeak'

        return equipment_point_record

    def get_all_for_account_between_dates(self, account_id, query_params):
        return self.uow.apply_query_parameters(self.table.get_all(account_id, index='account_id')
                                               .filter(r.row['readingdateutc'].during(
                                                        r.epoch_time(query_params.start_date),
                                                        r.epoch_time(query_params.end_date),
                                                        right_bound='closed')
                                                       ),
                                               query_params)

    def delete_for_syrx_num(self, syrx_num):
        self.uow.run(self.uow.tables.equipment_point_records.get_all(syrx_num, index='syrx_num').delete())

    def get_all_equipment_point_records_for_syrx_num(self, syrx_num):
        return self.uow.run_list(self.uow.tables.equipment_point_records.get_all(syrx_num, index='syrx_num'))

    def get_equipment_point_dates(self, syrx_num):
        return self.uow.run_list(self.uow.tables.equipment_point_records.get_all(syrx_num, index='syrx_num').pluck('date'))