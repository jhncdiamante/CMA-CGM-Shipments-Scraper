from .Website import Website, retry_until_success

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from .Shipment import Shipment
import logging
from .SearchBar import SearchBar
import time
import random
from ..Log.logging_config import setup_logger
setup_logger()


class CMA(Website):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.open_page(self._base_url)
        self._driver.maximize_window()
        self.search_bar = SearchBar(self._driver)

        self.shipments = [] # list of Shipment objects
        self.failed_shipments = []

    def start(self, shipment_ids: list[str]):
        for shipment_id in shipment_ids:
            
            self.search_bar.clear()
            self.search_bar.type_keyword(shipment_id)
            self.search_bar.click_search_button()
            time.sleep(random.randint(5, 10))
            try:
                self.shipments.append(Shipment(str(shipment_id), self._driver))
            except Exception as e:
                logging.error(f"Failed to process shipment {shipment_id}. Error: {e}")
                self.failed_shipments.append(shipment_id)
            finally:
                logging.info(f"Shipment {shipment_id} processed.")
                self.search_bar = SearchBar(self._driver)
                time.sleep(random.randint(10, 20))
                
    
