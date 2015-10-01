import logging
from logging.handlers import RotatingFileHandler
from nightly_process.calculated_point_handler import CalculatedPointHandler
from nightly_process.unmapped_syrx_num_handler import UnmappedSyrxNumHandler
from noaa_importer import noaa_importer
from nightly_process.numeric_point_handler import NumericPointHandler
import os
from vendor_data_pipeline.fieldserver_file_handler import FieldserverFileHandler
from vendor_data_pipeline.fieldserver_grouper import FieldserverGrouper
from vendor_data_pipeline.global_vendor_point_handler import GlobalVendorPointHandler
from vendor_data_pipeline.invensys_file_handler import InvensysFileHandler
from vendor_data_pipeline.invensys_grouper import InvensysGrouper
from vendor_data_pipeline.johnson_file_handler import JohnsonFileHandler
from vendor_data_pipeline.johnson_grouper import JohnsonGrouper
from vendor_data_pipeline.siemens_file_handler import SiemensFileHandler
from vendor_data_pipeline.siemens_grouper import SiemensGrouper
from vendor_data_pipeline.syrx_file_handler import SyrxFileHandler


class NightlyProcess:
    def __init__(self, config):
        self.config = config
        self.syrx_upload_folder = config.SYRX_UPLOAD_FOLDER

        self.johnson_raw_folder = config.JOHNSON_RAW_FOLDER
        self.johnson_grouped_folder = config.JOHNSON_GROUPED_FOLDER
        self.fieldserver_raw_folder = config.FIELDSERVER_RAW_FOLDER
        self.fieldserver_grouped_folder = config.FIELDSERVER_GROUPED_FOLDER
        self.invensys_raw_folder = config.INVENSYS_RAW_FOLDER
        self.invensys_grouped_folder = config.INVENSYS_GROUPED_FOLDER
        self.siemens_xml_folder = config.SIEMENS_XML_FOLDER
        self.siemens_raw_folder = config.SIEMENS_RAW_FOLDER
        self.siemens_grouped_folder = config.SIEMENS_GROUPED_FOLDER

        self.global_vendor_point_error_folder = config.GLOBAL_VENDOR_POINT_ERROR_FOLDER

        self.logger = self.get_logger(config)

    @staticmethod
    def get_logger(config):

        main_log = os.path.join(config.LOG_FOLDER, 'nightly_process.log')
        logger = logging.getLogger("nightly_process_logger")
        logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(main_log, maxBytes=100000, backupCount=10)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]')
        )
        logger.addHandler(handler)

        return logger

    def import_weather_data(self):
        noaa_importer.run(self.config)

    def group_vendor_data(self):
        self.logger.info("Nightly process group vendor data begin")

        self.group_johnson_files()
        self.group_fieldserver_files()
        self.group_invensys_files()
        self.group_siemens_files()

    def process_vendor_data(self):
        self.logger.info("Nightly process process vendor data begin")

        self.process_johnson_files()
        self.process_fieldserver_files()
        self.process_invensys_files()
        self.process_siemens_files()
        self.process_syrx_files()

    def handle_component_data(self):
        self.logger.info("Nightly process handle component data begin")

        self.handle_numeric_points()
        self.handle_calculated_points()

        self.logger.info("Finished handling component data")

    def group_johnson_files(self):
        johnson_grouper = JohnsonGrouper()
        johnson_grouper.johnson_raw_folder = self.johnson_raw_folder
        johnson_grouper.johnson_grouped_folder = self.johnson_grouped_folder
        johnson_grouper.logger = self.logger
        self.logger.info("Grouping johnson files")
        johnson_grouper.process_all_johnson_files()

    def group_fieldserver_files(self):
        fieldserver_grouper = FieldserverGrouper()
        fieldserver_grouper.fieldserver_raw_folder = self.fieldserver_raw_folder
        fieldserver_grouper.fieldserver_grouped_folder = self.fieldserver_grouped_folder
        fieldserver_grouper.logger = self.logger
        self.logger.info("Grouping Fieldserver files")
        fieldserver_grouper.process_all_fieldserver_files()

    def group_invensys_files(self):
        invensys_grouper = InvensysGrouper()
        invensys_grouper.invensys_raw_folder = self.invensys_raw_folder
        invensys_grouper.invensys_grouped_folder = self.invensys_grouped_folder
        invensys_grouper.logger = self.logger
        self.logger.info("Grouping Invensys files")
        invensys_grouper.process_all_invensys_files()

    def group_siemens_files(self):
        siemens_grouper = SiemensGrouper()
        siemens_grouper.siemens_xml_folder = self.siemens_xml_folder
        siemens_grouper.siemens_raw_folder = self.siemens_raw_folder
        siemens_grouper.siemens_grouped_folder = self.siemens_grouped_folder
        siemens_grouper.logger = self.logger
        self.logger.info("Grouping Siemens files")
        siemens_grouper.run()

    def process_johnson_files(self):
        johnson_file_handler = JohnsonFileHandler()
        johnson_file_handler.johnson_grouped_folder = self.johnson_grouped_folder
        johnson_file_handler.syrx_upload_folder = self.syrx_upload_folder
        johnson_file_handler.logger = self.logger
        self.logger.info("Processing johnson files")
        johnson_file_handler.run()

    def process_fieldserver_files(self):
        fieldserver_file_handler = FieldserverFileHandler()
        fieldserver_file_handler.fieldserver_grouped_folder = self.fieldserver_grouped_folder
        fieldserver_file_handler.syrx_upload_folder = self.syrx_upload_folder
        fieldserver_file_handler.logger = self.logger
        self.logger.info("Processing fieldserver files")
        fieldserver_file_handler.run()

    def process_invensys_files(self):
        invensys_file_handler = InvensysFileHandler()
        invensys_file_handler.invensys_grouped_folder = self.invensys_grouped_folder
        invensys_file_handler.syrx_upload_folder = self.syrx_upload_folder
        invensys_file_handler.logger = self.logger
        self.logger.info("Processing invensys files")
        invensys_file_handler.run()

    def process_siemens_files(self):
        siemens_file_handler = SiemensFileHandler()
        siemens_file_handler.siemens_grouped_folder = self.siemens_grouped_folder
        siemens_file_handler.syrx_upload_folder = self.syrx_upload_folder
        siemens_file_handler.logger = self.logger
        self.logger.info("Processing siemens files")
        siemens_file_handler.run()

    def process_syrx_files(self):
        syrx_file_handler = SyrxFileHandler()
        syrx_file_handler.syrx_upload_folder = self.syrx_upload_folder
        syrx_file_handler.logger = self.logger
        self.logger.info("Processing syrx files")
        syrx_file_handler.process_all_syrx_files()

    def handle_unmapped_syrx_nums(self):
        self.logger.info("Handling unmapped points")
        unmapped_syrx_num_handler = UnmappedSyrxNumHandler()
        unmapped_syrx_num_handler.logger = self.logger
        unmapped_syrx_num_handler.run()

    def handle_global_vendor_points(self):
        self.logger.info("Handling global vendor points")
        global_vendor_point_handler = GlobalVendorPointHandler()
        global_vendor_point_handler.logger = self.logger
        global_vendor_point_handler.error_folder = self.global_vendor_point_error_folder
        global_vendor_point_handler.process_all_global_vendor_points()

    def handle_calculated_points(self):
        self.logger.info("Handling calculated points")
        calculated_point_handler = CalculatedPointHandler()
        calculated_point_handler.logger = self.logger
        calculated_point_handler.run()

    def handle_numeric_points(self):
        self.logger.info("Handling numeric points")
        numeric_point_handler = NumericPointHandler()
        numeric_point_handler.logger = self.logger
        numeric_point_handler.run()

    def run(self):
        self.logger.info("Nightly process begin")

        self.import_weather_data()
        self.handle_unmapped_syrx_nums()
        self.group_vendor_data()
        self.process_vendor_data()
        self.handle_global_vendor_points()
        self.handle_component_data()
        self.logger.info("Nightly process end")