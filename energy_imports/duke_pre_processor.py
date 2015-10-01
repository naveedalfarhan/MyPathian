__author__ = 'amitkumar'
import csv
from datetime import datetime, timedelta
import tempfile
#from energy_imports.importer import EnergyImporter
import os
from time import mktime, strptime, strftime
import pytz
from pdb import set_trace as trace

ambig_two_am_hit = 0

def check_ambiguous(date):
    try:
        pytz.timezone("America/New_York").dst(date)
        return False
    except pytz.AmbiguousTimeError:
        return True
    except pytz.NonExistentTimeError:
        return False


def check_nonexistent(date):
    try:
        pytz.timezone("America/New_York").dst(date)
        return False
    except pytz.AmbiguousTimeError:
        return False
    except pytz.NonExistentTimeError:
        return True


def check_for_empty_row(row):
    """
    Checks if the row is empty and returns true if it is
    :param row:
    :return:
    """
    for item in row:
        if item != "":
            return False
    return True


def run(f):
    newfile = tempfile.TemporaryFile()
    f.seek(0)
    reader = csv.reader(f)
    writer = csv.writer(newfile)

    elec_record_map = {}
    gas_record_map = {}

    is_file_gas_type=False
    last_datetime = None
    blank_line_reached = False
    date_line_reached = False
    last_local_time = None
    last_unambiguous_date = None
    last_ambiguous_date = None
    after_repeat = False
    ambig_two_am = False

    for row in reader:
        if row[0]=='Time':
            is_file_gas_type=True
            writer.writerow(['DATE', 'mcf'])
            break
        if check_for_empty_row(row):
            blank_line_reached = True
            continue
        if blank_line_reached:
            if row[0] == 'DATE' and not date_line_reached:
                writer.writerow([row[0]] + row[2:])
                date_line_reached = True
            elif row[0] == 'DATE' and date_line_reached:
                continue
            else:
                date = get_reading_date(row[0], row[1], last_datetime)
                try:
                    data_insert = [date.strftime("%Y-%m-%d %H:%M")]
                except:
                    print "Error parsing date in row: " + ", ".join(row)
                    continue
                for entry in row[2:]:
                    data_insert += [float(entry)]
                if date in elec_record_map:
                    rec = elec_record_map[date]
                    for i in range(1, len(row) - 1):
                        rec[i] += float(data_insert[i])
                    elec_record_map[date] = rec
                else:
                    elec_record_map[date] = data_insert
                last_datetime = date

    if is_file_gas_type:
        for row in reader:
                eastern = pytz.timezone("America/New_York")
                try:
                    reading_date = datetime.fromtimestamp(mktime(strptime(row[0], "%m/%d/%Y %H:%M")))
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
    if is_file_gas_type:
        for key in sorted(gas_record_map):
            writer.writerow(gas_record_map[key])
    else:
        for key in sorted(elec_record_map):
            writer.writerow(elec_record_map[key])

    return newfile


def get_reading_date(date, time, last_datetime):
    eastern = pytz.timezone("America/New_York")

    if (len(date)) == 5:
        date = "0" + date

    if len(time) == 1:
        time = "000" + time
    elif len(time) == 2:
        time = "00" + time
    elif len(time) == 3:
        time = "0" + time

    is_hour_24 = False

    if time[0:2] == "24":
        time = "00" + time[2]
        is_hour_24 = True

    try:
        reading_date = datetime.fromtimestamp(mktime(strptime(date + time, "%m%d%y%H%M")))
    except:
        return None

    if is_hour_24:
        reading_date += timedelta(days=1)

    if check_nonexistent(reading_date):
        reading_date += timedelta(hours=1)

    ambig_millisecond = check_ambiguous(reading_date + timedelta(milliseconds=-1))
    ambig_reading_time = check_ambiguous(reading_date)

    ambig_time = ambig_millisecond or ambig_reading_time
    ambig_two_am = ambig_millisecond and not ambig_reading_time

    reading_date_utc = eastern.localize(reading_date).astimezone(pytz.UTC)

    if not ambig_time or not last_datetime:
        return reading_date_utc

    last_local_time = last_datetime.astimezone(eastern)

    yesterday_offset = eastern.utcoffset(eastern.localize(reading_date) + timedelta(days=-1))
    current_offset = eastern.utcoffset(eastern.localize(reading_date))
    tomorrow_offset = eastern.utcoffset(eastern.localize(reading_date) + timedelta(days=1))
    last_local_offset = last_local_time - last_datetime

    global ambig_two_am_hit

    if reading_date_utc.astimezone(eastern) > last_local_time and last_local_offset != tomorrow_offset:
        if 4 > ambig_two_am_hit > 0:
            reading_date_utc = eastern.localize(reading_date, is_dst=True).astimezone(pytz.UTC)
            ambig_two_am_hit += 1
        else:
            reading_date_utc = eastern.localize(reading_date).astimezone(pytz.UTC)
        if ambig_two_am:
            if 4 > ambig_two_am_hit:
                reading_date_utc = eastern.localize(reading_date + timedelta(minutes=-1), is_dst=True).astimezone(
                    pytz.UTC) + timedelta(hours=-1, minutes=1)
                ambig_two_am_hit += 1
            else:
                reading_date_utc = eastern.localize(reading_date).astimezone(pytz.UTC)
        elif not ambig_two_am and (ambig_two_am_hit > 4 or ambig_two_am_hit == 0):
            offset_to_add = current_offset - yesterday_offset
            reading_date_utc = eastern.localize(reading_date).astimezone(pytz.UTC) + offset_to_add
    return reading_date_utc
