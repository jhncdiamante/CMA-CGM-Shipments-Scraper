from selenium.webdriver.remote.webelement import WebElement


from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from Application.Website.Container import Container
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from .exceptions import ShipmentTimeoutError, ContainerNotFoundError, InvalidShipmentError


import logging

from ..Log.logging_config import setup_logger
from ..Website.Container import ContainerWithSiblings, ContainerWithNoSiblings
setup_logger()


TIMEOUT = 30

# Bill of Lading number pattern: exactly 9 digits
BILL_OF_LADING_PATTERN = r'^\d{9}$'

class Shipment:
    '''
    The Shipment class represents a single shipment, which is a collection of containers.
    Each shipment has one and only one shipment ID, and each shipment ID can, and oftentimes, have multiple containers.
    Each shipment has a tracking page in the website, thus, performing operations must be done on the shipment's tracking page.
    The shipment class is initialized by providing a shipment ID, and a WebDriver instance of the full page.
    '''
    def __init__(self, shipment_id: str, page: WebDriver):
            
        self.page = page
        self.shipment_id = shipment_id
        self.containers = self.get_containers()

    def get_containers(self) -> list[Container]: 
        logging.info("Getting containers...")
        try:
            
            containers = WebDriverWait(self.page, TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, "cardelem"))
            )
                
            logging.info(f"Found {len(containers)} containers.")
            
            return [ContainerWithSiblings(container, self.page) for container in containers]
            
        except TimeoutException as e:
            single_container = WebDriverWait(self.page, TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, "trackingsearchsection"))
            )
            logging.info(f"Found 1 container.")
            return [ContainerWithNoSiblings(single_container, self.page)]
        
        except Exception as e:
            raise ShipmentTimeoutError(self.shipment_id, "get_containers", str(e))

    
