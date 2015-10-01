import csv
from datetime import datetime, timedelta
from time import mktime, strptime
from energy_imports.importer import EnergyImporter
import os
import pytz


def check_ambiguous(date):
    try:
        pytz.timezone("America/New_York").dst(date)
        return False
    except pytz.AmbiguousTimeError:
        return True


def check_nonexistent(date):
    try:
        pytz.timezone("America/New_York").dst(date)
        return False
    except pytz.NonExistentTimeError:
        return True


def run(account_id):
    if not os.path.exists("C:/energy_imports/duke_gas/"):
        os.makedirs("C:/energy_imports/duke_gas")

    f = open('bethesda_oak_gas.csv', 'rb')
    new_file = open('C:/energy_imports/duke_gas/' + f.name, 'wb+')
    reader = csv.reader(f)
    writer = csv.writer(new_file)

    gas_record_map = {}

    last_local_time = None
    last_unambiguous_date = None
    last_ambiguous_date = None
    after_repeat = False
    ambig_two_am = False
    for row in reader:
        if row[0] == 'Time':
            writer.writerow(['DATE', 'mCf'])
        else:
            eastern = pytz.timezone("America/New_York")

            try:
                reading_date = datetime.fromtimestamp(mktime(strptime(row[0], "%Y-%m-%d %H:%M:%S")))
            except:
                continue

            ambiguous_time = check_ambiguous(reading_date)

            reading_date = eastern.localize(reading_date)
            reading_date_utc = reading_date.astimezone(pytz.UTC)

            if ambiguous_time:
                yesterday_offset = eastern.utcoffset(reading_date + timedelta(days=-1))
                current_offset = eastern.utcoffset(reading_date)
                tomorrow_offset = eastern.utcoffset(reading_date + timedelta(days=1))

                if not after_repeat:
                    temp_date_utc = reading_date.astimezone(pytz.UTC) + timedelta(hours=-1)
                    temp_date_local = temp_date_utc.astimezone(eastern)

                    if last_ambiguous_date and temp_date_local <= last_ambiguous_date:
                        after_repeat = True
                    else:
                        last_ambiguous_date = temp_date_local
                        reading_date = temp_date_local
                        reading_date_utc = temp_date_utc
                if after_repeat:
                    reading_date_utc = reading_date.astimezone(pytz.UTC) - (
                        current_offset - tomorrow_offset)
                    reading_date = reading_date_utc.astimezone(eastern)

            else:
                if after_repeat:
                    last_ambiguous_date = None
                    after_repeat = False
                last_unambiguous_date = reading_date

            mcf = 0.0
            for entry in row[1:]:
                mcf += float(entry)

            if last_local_time and last_local_time and not reading_date and not after_repeat and last_unambiguous_date == reading_date:
                this_reading_date_utc = reading_date_utc + timedelta(hours=1)

                if this_reading_date_utc in gas_record_map:
                    rec = gas_record_map[this_reading_date_utc]
                    rec[1] += mcf
                    gas_record_map[this_reading_date_utc] = rec
                else:
                    gas_record_map[this_reading_date_utc] = [this_reading_date_utc.strftime("%Y-%m-%d %H:%M"), mcf]
            else:
                if reading_date_utc in gas_record_map:
                    rec = gas_record_map[reading_date_utc]
                    rec[1] += mcf
                    gas_record_map[reading_date_utc] = rec
                else:
                    gas_record_map[reading_date_utc] = [reading_date_utc.strftime("%Y-%m-%d %H:%M"), mcf]

            last_local_time = reading_date

    for key in sorted(gas_record_map):
        writer.writerow(gas_record_map[key])

    f.close()
    new_file.close()

    EnergyImporter().run(account_id, os.path.abspath(new_file.name))


if "__main__" == __name__:
    run("71d7aad5-2f91-4cfa-9388-749451139191")