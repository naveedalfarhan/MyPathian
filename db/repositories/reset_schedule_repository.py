from api.models.ResetSchedule import ResetSchedule

class ResetScheduleRepository:
    def __init__(self, uow):
        self.uow = uow
        self.reset_schedules_table = uow.tables.reset_schedules

    def get_all(self, query_parameters):
        return self.uow.apply_query_parameters(self.reset_schedules_table, query_parameters)

    def get_all_reset_schedules(self):
        return self.uow.run(self.reset_schedules_table.order_by('name'))

    def get(self, reset_schedule_id):
        model_raw = self.uow.run(self.reset_schedules_table.get(reset_schedule_id))
        model = ResetSchedule(model_raw)
        return model

    def insert(self, model):
        try:
            del model.id
        except AttributeError:
            pass
        result = self.uow.run(self.reset_schedules_table.insert(model.__dict__))
        reset_schedule_id = result["generated_keys"][0]
        return reset_schedule_id

    def update(self, model):
        self.uow.run(self.reset_schedules_table.update(model.__dict__))

    def delete(self, reset_schedule_id):
        self.uow.run(self.reset_schedules_table.get(reset_schedule_id).delete())

    def get_all_as_list(self):
        return self.uow.run(self.reset_schedules_table)
