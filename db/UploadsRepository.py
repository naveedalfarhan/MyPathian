import uuid
from api.models.import_thread import ImportThread
from energy_imports.importer import EnergyImporter
from import_from_master_spreadsheet import MasterSpreadsheetImporter


class UploadsRepository:

    import_threads = []

    @classmethod
    def get_all(cls):
        return cls.import_threads

    @classmethod
    def start_import(cls, account_id, uploaded_file_handle, uploaded_file_type):
        importer = EnergyImporter(account_id, uploaded_file_handle, uploaded_file_type)

        import_thread = ImportThread(importer)
        import_thread.start()

        thread_obj = {
            "id": uuid.uuid4(),
            "thread": import_thread
        }
        cls.import_threads.append(thread_obj)
        return thread_obj["id"]

    @classmethod
    def upload_components(cls, file_handle):
        importer = MasterSpreadsheetImporter(file_handle)
        importer.run()
        #import_thread = ImportThread(importer)
        #import_thread.start()