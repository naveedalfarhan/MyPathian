from config import BaseConfig
from nightly_process.main import NightlyProcess

nightly_process = NightlyProcess(BaseConfig)
nightly_process.run()