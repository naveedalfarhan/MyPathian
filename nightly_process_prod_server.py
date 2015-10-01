from config import ProdServerConfig
from nightly_process.main import NightlyProcess

nightly_process = NightlyProcess(ProdServerConfig)
nightly_process.run()