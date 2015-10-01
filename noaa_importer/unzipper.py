import gzip
import tempfile


class Unzipper:
    def __init__(self, gz_file_path):
        self.gz_file_path = gz_file_path
        self.unzipped_file_path = None

    def run(self):
        f = gzip.open(self.gz_file_path, "rb")
        file_content = f.read()
        f.close()

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(file_content)
        self.unzipped_file_path = temp_file.name
        temp_file.close()