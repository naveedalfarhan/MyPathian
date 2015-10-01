from datetime import datetime
import pytz


class BronzeReportingRepository:
    def __init__(self, uow):
        self.uow = uow
        self.table = uow.tables.bronze_reporting_requests

    def get_submissions(self):
        data = self.uow.run_list(self.table)
        for d in data:
            d["saved_on"] = d["saved_on"].strftime("%Y-%m-%d %H:%M:%S")
        return data

    def get_submission(self, submission_id):
        model = self.uow.run(self.table.get(submission_id))
        return model

    def save_submission(self, model, electric_file_contents, gas_file_contents):
        model["saved_on"] = pytz.utc.localize(datetime.utcnow())
        model["processing_state"] = "submitted"
        if electric_file_contents is not None:
            model['electricAccount']["file"] = electric_file_contents
        if gas_file_contents is not None:
            model['gasAccount']["file"] = gas_file_contents

        self.uow.run(self.table.insert(model))

    def change_submission_state(self, submission_id, processing_state):
        model = self.uow.run(self.table.get(submission_id))

        model["processing_state"] = processing_state
        self.uow.run(self.table.get(submission_id).update(model))

        return model


