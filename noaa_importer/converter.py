import shutil
import os
import subprocess
import tempfile
import pkg_resources


class Converter:
    def __init__(self, encoded_file_path):
        self.encoded_file_path = encoded_file_path
        self.unencoded_file_path = None
        self.original_path = None
        self.temp_dir = None

    def change_to_temp_dir(self):
        self.original_path = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def change_to_original_dir(self):
        os.chdir(self.original_path)
        shutil.rmtree(self.temp_dir)

    def copy_java_source_file(self):
        ish_java_path = pkg_resources.resource_filename("noaa_importer", os.path.join("utilities", "ishJava.java"))
        shutil.copy(ish_java_path, self.temp_dir)

    def compile(self):
        subprocess.call(['javac', "ishJava.java"])

    def run_java(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        subprocess.call(['java', '-classpath', '.', 'ishJava', self.encoded_file_path, temp_file.name])
        self.unencoded_file_path = temp_file.name

    def run(self):
        self.change_to_temp_dir()
        self.copy_java_source_file()
        self.compile()
        self.run_java()
        self.change_to_original_dir()