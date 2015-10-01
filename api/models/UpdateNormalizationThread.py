from threading import Thread
from compile_energy_records import EnergyRecordCompiler
from db.uow import UoW


class UpdateNormalizationThread(Thread):
    def __init__(self, norm_type, normalization):
        self.compiler = EnergyRecordCompiler()
        self.norm_type = norm_type
        self.normalization = normalization
        self.uow = UoW(None)
        super(UpdateNormalizationThread, self).__init__()

    def run(self):
        if self.norm_type.lower() == "size":
            end_date = self.uow.energy_records.update_size_norms(self.normalization)
        elif self.norm_type.lower() == "price":
            end_date = self.uow.energy_records.update_price_norms(self.normalization)
        else:
            raise Exception("The type specified is invalid.")
        self.compiler.compile_energy_records_by_date_span(self.normalization.effective_date, end_date, self.normalization.account_id)