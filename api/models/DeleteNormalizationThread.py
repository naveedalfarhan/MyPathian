from threading import Thread
from compile_energy_records import EnergyRecordCompiler
from db.uow import UoW


class DeleteNormalizationThread(Thread):
    def __init__(self, norm_type, normalization):
        self.uow = UoW(None)
        self.compiler = EnergyRecordCompiler()
        self.norm_type = norm_type
        self.normalization = normalization
        super(DeleteNormalizationThread, self).__init__()

    def run(self):
        if self.norm_type.lower() == "size":
            end_date = self.uow.energy_records.update_size_normalizations_from_delete(self.normalization)
            self.uow.size_normalizations.delete(self.normalization.id)
        elif self.norm_type.lower() == "price":
            end_date = self.uow.energy_records.update_price_normalizations_from_delete(self.normalization)
            self.uow.price_normalizations.delete(self.normalization.id)
        else:
            raise Exception('The specified type is invalid.')

        self.compiler.compile_energy_records_by_date_span(self.normalization.effective_date, end_date, self.normalization.account_id)