from collections import defaultdict
from datetime import datetime
from api.models.Account import Account


class AccountRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.accounts

    def get_all(self, query_parameters=None):
        if query_parameters is None:
            return self.uow.run_list(self.table)
        return self.uow.apply_query_parameters(self.table, query_parameters)

    def get_all_by_group_id(self, query_parameters, group_id):
        return self.uow.apply_query_parameters(self.table.get_all(group_id, index="group_id"), query_parameters)

    def get_by_id(self, model_id):
        model_raw = self.uow.run(self.table.get(model_id))
        if model_raw is None:
            return None
        model = Account(model_raw)
        return model

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass

        result = self.uow.run(self.table.insert(model.__dict__))
        model.id = result["generated_keys"][0]
        return model.id

    def update(self, model):
        d = model.__dict__
        self.uow.run(self.table.get(model.id).update(d))

    def delete(self, model_id):
        self.uow.run(self.table.get(model_id).delete())

    def insert_batch(self, accounts):
        self.uow.run(self.table.insert(accounts))

    def delete_all(self):
        self.uow.run(self.table.delete())

    def get_all_pricenormalizations_for_account(self, account_id, query_parameters):
        table = self.table.get(account_id).concat_map(lambda x: x["pricenormalizations"])
        return self.uow.apply_query_parameters(table, query_parameters)

    def add_pricenormalization(self, account_id, pricenormalization):
        normalizations = self.table.get(account_id)["pricenormalizations"].default([]).append(pricenormalization)
        self.uow.run(self.table.get(account_id).update({"pricenormalizations": normalizations}, non_atomic=True))

    def update_pricenormalization(self, account_id, pricenormalization):
        self.table.get(account_id).concat_map(lambda x: x["pricenormalizations"]).filter({"id": pricenormalization.id})

    def get_by_group_id_and_account_type(self, group_id, acc_type=None):
        if acc_type:
            accounts = self.uow.run_list(self.table.get_all(group_id, index='group_id').filter({'type': acc_type}))
        else:
            accounts = self.uow.run_list(self.table.get_all(group_id, index='group_id'))
        return accounts

    def get_all_for_group(self, group_id):
        accounts = self.uow.run_list(self.table.get_all(group_id, index='group_id'))
        return accounts

    def check_alarm(self, account_id):
        current_date = datetime.now()

        report_month_query = (self.uow.tables.compiled_energy_records
                              .get_all([account_id, current_date.year, current_date.month, 'temp'],
                                       index='account_year_month')
                              .group(lambda record: {'temp': record['comparison_value']})
                              .map(lambda record: {'btu': record['sum_btu'], 'hrs': record['sum_hours_in_record']})
                              .reduce(lambda a, b: {'btu': a['btu'] + b['btu'], 'hrs': a['hrs'] + b['hrs']})
                              .ungroup())

        report_month_records = self.uow.run_list(report_month_query)

        # get the previous years records, filtering out records that
        # do not have a matching temperature in the report month

        previous_year_query = (self.uow.tables.compiled_energy_records
                               .get_all([account_id, current_date.year - 1, 'temp'], index='account_year')
                               .inner_join(self.uow.tables.compiled_energy_records
                                           .get_all([account_id, current_date.year, current_date.month, 'temp'],
                                                    index='account_year_month'),
                                           lambda a_row, b_row: a_row['comparison_value'] == b_row['comparison_value'])
                               .map(lambda record: record['left'])
                               .group(lambda record: {'temp': record['comparison_value']})
                               .map(lambda record: {'btu': record['sum_btu'], 'hrs': record['sum_hours_in_record']})
                               .reduce(lambda a, b: {'btu': a['btu'] + b['btu'], 'hrs': a['hrs'] + b['hrs']})
                               .ungroup())

        previous_year_records = self.uow.run_list(previous_year_query)

        year_group = defaultdict(dict)

        # group everything into a dictionary keyed by temperature
        for entry in previous_year_records:
            year_group[entry['group']['temp']] = entry

        simulated_benchmark_consumption = 0.0
        simulated_report_consumption = 0.0
        for r in report_month_records:
            # ensure that the records are correct
            if r['group']['temp'] in year_group:
                previous_year_record = year_group[r['group']['temp']]
                # convert BTU to BTU/hr, then convert to kW
                prev_year_demand = (previous_year_record['reduction']['btu'] / previous_year_record['reduction'][
                    'hrs']) / 3412.142
                simulated_benchmark_consumption += (prev_year_demand * r['reduction']['hrs'])
                prev_month_demand = (r['reduction']['btu'] / r['reduction']['hrs']) / 3412.142
                simulated_report_consumption += (prev_month_demand * r['reduction']['hrs'])

        percent_change = (simulated_report_consumption / simulated_benchmark_consumption) - 1

        threshold = self.uow.run(self.table.get(account_id))['deviation_threshold']

        if percent_change > threshold / 100.0:
            return True
        else:
            return False

    def add_notification(self, user_id, account_id):
        """
        Adds notification to active_notifications table
        """
        notifications_exist = not self.uow.run(self.uow.tables.active_notifications
                                               .get_all([user_id, account_id], index='unique_notification').is_empty())

        if not notifications_exist:
            account = self.get_by_id(account_id)
            self.uow.run(self.uow.tables.active_notifications
                         .insert({'user_id': user_id,
                                  'text': account.name +
                                          ' is reporting a higher consumption rate than the threshold allows.'}))
        else:
            return_data = []
            dashboard_notifications = self.uow.run_list(self.uow.tables.active_notifications
                                                        .get_all([user_id, account_id, 'dashboard'], index='type'))

            for notification in dashboard_notifications:
                if notification['status'] == 'enabled':
                    return_data.append(notification['text'])
            return return_data
