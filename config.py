import os
from utils import make_dir, get_sys_root_path


class BaseConfig(object):
    PROJECT = "pathian"
    DEBUG = True
    TESTING = True
    MINIFY = False
    CACHE_TYPE = "null"

    LOG_FOLDER = get_sys_root_path() + "pathian-logs"
    UPLOAD_FOLDER = get_sys_root_path() + "pathian-uploads"
    REPORT_FOLDER = get_sys_root_path() + "pathian-reports"
    BRONZE_REPORTING_FOLDER = get_sys_root_path() + "pathian-bronze-reporting"

    SYRX_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "general-component")

    JOHNSON_RAW_FOLDER = os.path.join(UPLOAD_FOLDER, "johnson", "raw")
    JOHNSON_GROUPED_FOLDER = os.path.join(UPLOAD_FOLDER, "johnson", "grouped")
    FIELDSERVER_RAW_FOLDER = os.path.join(UPLOAD_FOLDER, "fieldserver", "raw")
    FIELDSERVER_GROUPED_FOLDER = os.path.join(UPLOAD_FOLDER, "fieldserver", "grouped")
    INVENSYS_RAW_FOLDER = os.path.join(UPLOAD_FOLDER, "invensys", "raw")
    INVENSYS_GROUPED_FOLDER = os.path.join(UPLOAD_FOLDER, "invensys", "grouped")
    SIEMENS_XML_FOLDER = os.path.join(UPLOAD_FOLDER, "siemens", "xml")
    SIEMENS_RAW_FOLDER = os.path.join(UPLOAD_FOLDER, "siemens", "raw")
    SIEMENS_GROUPED_FOLDER = os.path.join(UPLOAD_FOLDER, "siemens", "grouped")

    GLOBAL_VENDOR_POINT_ERROR_FOLDER = os.path.join(UPLOAD_FOLDER, "gvp", "errors")

    MANDRILL_API_KEY = "q2i2UJzZROM63sPgFIo91g"

    DB_NAME = "pathian"
    DB_HOST = "localhost"
    DB_PORT = 28015


class DefaultConfig(BaseConfig):
    MINIFY = False


class TestConfig(BaseConfig):
    TESTING = True


class DevServerConfig(BaseConfig):
    DB_HOST = "localhost"
    DEBUG = True


class ProdServerConfig(BaseConfig):
    DB_HOST = "localhost"

    MANDRILL_API_KEY = "Crs08iVe9NV6Ssn3RWPk_Q"
    DEBUG = True
    MINIFY = True
    LOG_FOLDER = "/var/log/pathian"
    UPLOAD_FOLDER = "/pathian/uploads"
    REPORT_FOLDER = "/pathian/pathian-reports"
    BRONZE_REPORTING_FOLDER = "/pathian/uploads/bronze"

    SYRX_UPLOAD_FOLDER = "/pathian/uploads/syrx"

    JOHNSON_RAW_FOLDER = "/pathian/uploads/johnson/raw"
    JOHNSON_GROUPED_FOLDER = "/pathian/uploads/johnson/grouped"
    FIELDSERVER_RAW_FOLDER = "/pathian/uploads/fieldserver/raw"
    FIELDSERVER_GROUPED_FOLDER = "/pathian/uploads/fieldserver/grouped"
    INVENSYS_RAW_FOLDER = "/pathian/uploads/invensys/raw"
    INVENSYS_GROUPED_FOLDER = "/pathian/uploads/invensys/grouped"
    SIEMENS_XML_FOLDER = "/home/siemens_energy/point_dump"
    SIEMENS_RAW_FOLDER = "/pathian/uploads/siemens/raw"
    SIEMENS_GROUPED_FOLDER = "/pathian/uploads/siemens/grouped"

    GLOBAL_VENDOR_POINT_ERROR_FOLDER = "/pathian/uploads/gvp/errors"