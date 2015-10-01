import sys
from config import BaseConfig
from noaa_importer import noaa_importer


def run(forced_weatherstation_id, forced_year):
    noaa_importer.run(BaseConfig, forced_weatherstation_id, forced_year)

def print_usage():
    print("noaa_importer [--weatherstation_id <weatherstation_id>] [--year <year>]")

try:
    weatherstation_id = None
    year = None
    arg_index = 1
    while arg_index < len(sys.argv):
        print "argument passed to fucntion"
        if sys.argv[arg_index] == "--weatherstation_id":
            weatherstation_id = sys.argv[arg_index + 1]
            arg_index += 2
        elif sys.argv[arg_index] == "--year":
            year = sys.argv[arg_index + 1]
            arg_index += 2
        else:
            print "in exception"
            raise Exception
    run(weatherstation_id, year)
except:
    print_usage()
    sys.exit(2)
