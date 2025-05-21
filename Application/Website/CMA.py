
from .Subject import Subject
from .Shipment import Shipment
import logging
from .SearchBar import SearchBar
import time
import random
from ..Log.logging_config import setup_logger     
from ..Observers.Application import Application
from Application.WebDriver.Driver import Driver

setup_logger()


class CMA(Subject):
    def __init__(self, base_url: str, driver: Driver):
        Subject.__init__(self)

        self.base_url = base_url
        self._driver = driver

        self.open_page(self._base_url)
        self.search_bar = SearchBar(self._driver)
        self._shipment = None

    @property
    def shipment(self):
        return self._shipment

    @shipment.setter
    def shipment(self, value: Shipment):
        self._shipment = value
        self.notify()


    def start(self, shipment_ids: list[str]):
        
        self._driver.maximize_window()
        for shipment_id in shipment_ids:
            
            self.search_bar.clear()
            self.search_bar.type_keyword(shipment_id)
            self.search_bar.click_search_button()
            time.sleep(random.randint(5, 10))
            try:
                self._shipment = Shipment(str(shipment_id), self._driver)
            except Exception as e:
                logging.error(f"Failed to process shipment {shipment_id}. Error: {e}")
                self.failed_shipments.append(shipment_id)
            finally:
                logging.info(f"Shipment {shipment_id} processed.")
                self.search_bar = SearchBar(self._driver)
                time.sleep(random.randint(10, 20))

    def close(self):
        self._driver.close()
                
    
if __name__ == "__main__":
    cma = CMA("https://www.cma-cgm.com/ebusiness/tracking/search")
    cma.start(["GHC0308970"])