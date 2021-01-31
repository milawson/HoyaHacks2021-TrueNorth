import csv

class DatabaseComponent:

    def __init__(self, csv_file_name):
        self.csv_file_name = csv_file_name

    def fetch(self):
        data = []
        first_row = True

        with open(self.csv_file_name, encoding="utf8") as csv_file:
            csv_file_reader = csv.reader(csv_file)
            for row in csv_file_reader:
                if first_row:
                    first_row = False
                    continue
                data.append(tuple(row))

        return data


