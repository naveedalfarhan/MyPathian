import csv
import json
import datetime
import os
import pytz
from vendor_data_pipeline.post_handler import round_time

fieldserver_folder = "C:\\pathian-uploads\\fieldserver"


file_names = os.listdir(fieldserver_folder)

for i, file_name in enumerate(file_names):
    try:
        print("Processing file " + str(i + 1) + "/" + str(len(file_names)))
        file_path = os.path.join(fieldserver_folder, file_name)

        file_name_date = file_name.split("_")[0].split("-")[1:4]
        file_name_time = file_name.split("_")[1:4]

        timestamp = pytz.utc.localize(datetime.datetime(int(file_name_date[0]), int(file_name_date[1]),
                                                        int(file_name_date[2]), int(file_name_time[0]),
                                                        int(file_name_time[1]), int(file_name_time[2])))
        timestamp = round_time(timestamp)

        file_name_date_str = "-".join(file_name_date)
        write_file_path = os.path.join(fieldserver_folder, file_name_date_str)

        with open(write_file_path, "a") as write_file:
            with open(file_path, "r") as f:
                data = json.loads(f.read())

                for (key, values) in data.iteritems():
                    key_split = key.split("_")
                    if key_split[1] == "Offsets":
                        site_id = key_split[0]
                        values_array = [float(r) for r in values.split(",")]
                        starting_offset = int(key_split[2].split("-")[0])

                        for offset, value in enumerate(values_array):
                            data = json.dumps({
                                "site_id": site_id,
                                "offset": starting_offset + offset,
                                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "value": value
                            })

                            write_file.write(data + u"\n")

        os.remove(file_path)
    except:
        pass