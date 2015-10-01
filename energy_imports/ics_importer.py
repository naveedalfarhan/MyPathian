import csv


def import_file(path):
    f = open(path, "rb")
    reader = csv.reader(f)
    for row in reader:
        time = row[0]
        group = row[1]
        equipment = row[2]
        point = row[3]
        value = row[4]
        print(time)

if "__main__" == __name__:
    import_file("sample_ics_file.csv")
