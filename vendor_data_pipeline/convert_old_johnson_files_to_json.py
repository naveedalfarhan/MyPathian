import csv
import json
import os

johnson_folder = "D:\\pathian-uploads\\johnson\\raw"


file_names = os.listdir(johnson_folder)

for i, file_name in enumerate(file_names):
    try:
        print("Processing file " + str(i + 1) + "/" + str(len(file_names)))
        file_path = os.path.join(johnson_folder, file_name)

        file_name_date = "-".join(file_name.split("_")[0].split("-")[1:4])
        write_file_path = os.path.join(johnson_folder, file_name_date)

        with open(write_file_path, "a") as write_file:
            with open(file_path, "r") as f:
                reader = csv.reader(f)

                for r in reader:
                    if reader.line_num == 1:
                        continue
                    new_record = {
                        "site_id": r[0],
                        "fqr": r[1],
                        "timestamp": r[2],
                        "value": r[3],
                        "reliability": r[4]
                    }

                    write_file.write(json.dumps(new_record) + "\n")

        os.remove(file_path)
    except:
        pass