from threading import Thread


class ImportThread(Thread):
    def __init__(self, importer):
        self.importer = importer
        super(ImportThread, self).__init__()

    def run(self):
        self.importer.run()