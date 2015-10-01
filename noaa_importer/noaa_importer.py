from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
from config import BaseConfig
from db.uow import UoW
import os
from downloader import Downloader
import pytz
from unzipper import Unzipper
from converter import Converter
from importer import Importer


class NoaaImportController:
    def __init__(self, ws, year, logger):
        self.logger = logger
        self.logger.debug("NoaaImportController initialized with ws = " + ws.name + ", year = " + str(year))
        self.ws = ws
        self.year = year
        self.uow = UoW(None)

    def run(self):
        self.logger.info("NoaaImportController.run started")
        print("NoaaImportController.run started")

        start_after_date = self.uow.weather_stations.get_last_record_time(self.ws.id, self.year)
        if start_after_date:
            next_date = start_after_date + timedelta(hours=1)
            if self.year < next_date.year:
                self.logger.info("Skipping year " + str(self.year))
                print("Skipping year " + str(self.year))
                return

        self.logger.debug("Downloader started")
        downloader = Downloader(self.ws.usaf, self.ws.wban, self.year)
        downloader.run()
        self.logger.debug("Downloader ended")

        self.logger.debug("Unzipper started")
        unzipper = Unzipper(downloader.downloaded_file_path)
        unzipper.run()
        os.unlink(downloader.downloaded_file_path)
        self.logger.debug("Unzipper ended")

        self.logger.debug("Converter started")
        converter = Converter(unzipper.unzipped_file_path)
        converter.run()
        os.unlink(unzipper.unzipped_file_path)
        self.logger.debug("Converter ended")

        self.logger.debug("Importer started")
        importer = Importer(self.ws.id, self.year, start_after_date, converter.unencoded_file_path)
        importer.run()
        os.unlink(converter.unencoded_file_path)
        self.logger.debug("Importer ended")

        self.logger.info("NoaaImportController.run ended")
        print("NoaaImportController.run ended")


def get_logger(config):
    main_log = os.path.join(config.LOG_FOLDER, 'noaa_importer.log')
    new_logger = logging.getLogger("noaa_importer")
    new_logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(main_log, maxBytes=100000, backupCount=10)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    new_logger.addHandler(handler)

    return new_logger


def run(config, forced_weatherstation_id=None, forced_year=None):
    logger = get_logger(config)
    uow = UoW(None)
    current_year = datetime.now().year
    weatherstations = uow.weather_stations.get_all()

    if forced_weatherstation_id:
        weatherstations = [ws for ws in weatherstations if ws.id == forced_weatherstation_id]

    weatherstation_count = len(weatherstations)
    weatherstation_counter = 0
    for ws in weatherstations:
        weatherstation_counter += 1
        years = range(current_year - 9, current_year + 1)
        if forced_year:
            years = [forced_year]
        for year in years:
            weatherstation_progress = "(" + str(weatherstation_counter) + "/" + str(weatherstation_count) + ")"
            weatherstation_tagline = ws.name + " " + weatherstation_progress + " for year " + str(year)
            try:
                logger.info("Importing " + weatherstation_tagline)
                print("Importing " + weatherstation_tagline)

                import_controller = NoaaImportController(ws, year, logger)
                import_controller.run()

                try:
                    weatherstation_years = set(ws.years)
                except:
                    weatherstation_years = set()
                weatherstation_years.add(year)
                ws.years = list(weatherstation_years)
                uow.weather_stations.update(ws)

                logger.info("Successfully imported " + weatherstation_tagline)
                print("Successfully imported " + weatherstation_tagline)
            except Exception, e:
                logger.exception("FAILED import " + weatherstation_tagline)
                print("FAILED import " + weatherstation_tagline)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename="noaa_importer.log", level=logging.DEBUG)
    run(BaseConfig)

