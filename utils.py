import sys
import os
from datetime import datetime

INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance')


def get_current_time():
    return datetime.utcnow()


def make_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except Exception, e:
        raise e


def get_sys_root_path():
    path = sys.executable
    while os.path.split(path)[1]:
        path = os.path.split(path)[0]
    return path