import re
from typing import Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.common.exceptions import NoSuchElementException

from ..Log.logging_config import setup_logger
setup_logger()

TIMEOUT = 30
class Milestone:
    def __init__(self, milestone_element: WebElement):
        self.milestone_element = milestone_element
        self.date: str = self.get_date()
       
        self.event: str = self.get_event()

        self.vessel_id, self.vessel_name = self.get_vessel_info()
        self.event = self.normalize_event()
        logging.info(f"Extracted milestone: {self.event} on {self.date} for vessel {self.vessel_name} with ID {self.vessel_id}")
        
    def get_vessel_info(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            vessel_voyage_element = self.milestone_element.find_element(By.CSS_SELECTOR, 'td.vesselVoyage.k-table-td')

            vessel_name = vessel_voyage_element.find_element(By.XPATH, './/a[1]').text.strip()

            # Extract the voyage reference (second <a> element text)
            voyage_reference = vessel_voyage_element.find_element(By.XPATH, './/a[2]').text
            match = re.search(r'\(\s*(\S+)\)', voyage_reference)

            voyage_reference = match.group(1) if match else ''
        except NoSuchElementException:
            voyage_reference = None
            vessel_name = None

        # Combine both into a single string
        return voyage_reference, vessel_name
    
    def get_event(self) -> str:
        return self.milestone_element.find_element(By.CSS_SELECTOR, 'span.capsule').text.strip()
    
    def get_date(self) -> str:
        date_time_element = WebDriverWait(self.milestone_element, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'td.date.k-table-td')))

        return date_time_element.find_element(By.CSS_SELECTOR, '.calendar').text + ' ' + date_time_element.find_element(By.CSS_SELECTOR, '.time').text


    def normalize_event(self) -> str:
        events = {
            'READY TO BE LOADED': 'Gate in',
            'VESSEL DEPARTURE': 'Departure',
            'VESSEL ARRIVAL': 'Arrival',
            'DISCHARGED IN TRANSHIPMENT': 'Discharge',
            'CONTAINER TO CONSIGNEE': 'Pull Out'
        }

        return events.get(self.event.upper(), self.event)


    