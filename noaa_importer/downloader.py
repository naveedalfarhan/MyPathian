from ftplib import FTP
import tempfile


class Downloader:
    def __init__(self, usaf, wban, year):
        self.usaf = usaf
        self.wban = wban
        self.year = year
        self.downloaded_file_path = None

    def run(self):
        ftp = FTP("ftp.ncdc.noaa.gov", "anonymous", "sprice@productivity.rippe.com")
        dir = "/pub/data/noaa/" + str(self.year)
        remote_filename = str(self.usaf) + "-" + str(self.wban) + "-" + str(self.year) + ".gz"
        ftp.cwd(dir)

        file = tempfile.NamedTemporaryFile(delete=False)
        ftp.retrbinary("RETR " + remote_filename, file.write)

        ftp.close()

        self.downloaded_file_path = file.name
        file.close()