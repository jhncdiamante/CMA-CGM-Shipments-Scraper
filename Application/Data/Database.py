import csv
import os


FIELDNAMES = ["Shipment ID", "Container ID", 'Gate in', 'Departure', 'Arrival', 'Discharge', 'Gate out',
              "Status", "ETA", "Scraped at"]

class Database():
    def __init__(self, file_path: str):
        self.file_path = file_path

    def update(self, container_data: dict):
        file_exists = os.path.isfile(self.file_path)
        is_empty = os.stat(self.file_path).st_size == 0 if file_exists else True

        with open(self.file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)

            if is_empty:
                writer.writeheader()  # Write headers only if file is new or empty

            writer.writerow(container_data)  # Append one row of data
