from ..Data.Database import Database
from ..Website.Subject import Subject
from datetime import datetime



DATABASE_FILE_PATH = "OUTPUT.csv"
MILESTONE_KEYS = ['Gate in', 'Departure', 'Arrival', 'Discharge', 'Gate out']
ONGOING_MILESTONE_KEYS = MILESTONE_KEYS[:2]

class Application(Subject):
    def __init__(self):
        super().__init__()
        self._container_data: dict = None
        self.attach(Database(DATABASE_FILE_PATH))

    @property
    def container_data(self):
        return self._container_data

    @container_data.setter
    def container_data(self, value: dict):
        self._container_data = value
        self.notify()

    def update(self, subject):
        shipment_id = subject.shipment.id
        for container in subject.containers:
            container_id = container.id
            m_keys = MILESTONE_KEYS if container.get_status() else ONGOING_MILESTONE_KEYS

            container_data = {"Shipment ID": shipment_id,
                              "Container ID": container_id,
                              "Gate in": None,
                              "Arrival": None,
                              "Departure": None,
                              "Discharge": None,
                              "Gate out": None}
            for milestone in container.milestones:
                if milestone.event not in m_keys:
                        continue  # skip unnecessary milestones

                    # this control flow records the first occurrence of Gate in and Departure
                    # and the last occurrence of Arrival, Discharge, and Gate out for delivery

                if (container_data[milestone.event] is not None and milestone.event not in ONGOING_MILESTONE_KEYS) or (container_data[milestone.event] is None):
                    container_data[milestone.event] = milestone.date
                    if milestone.event in ["Arrival", "Departure"]:
                        container_data[f"{milestone.event} Vessel Name"] = milestone.vessel_name
                        container_data[f"{milestone.event} Voyage ID"] = milestone.vessel_id 

            container_data["Status"] = "Completed" if container.get_status() else "On-going"
            container_data["ETA"] = container.eta

            container_data['Scraped at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self._container_data = container_data

