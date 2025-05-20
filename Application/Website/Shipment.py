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
import re
setup_logger()
from .helpers import retryable


TIMEOUT = 30


CONTAINER_CLASS_NAME = "cardelem"
SINGLE_CONTAINER_ID = "trackingsearchsection"

class Shipment:
    '''
    The Shipment class represents a single shipment, which is a collection of containers.
    Each shipment has one and only one shipment ID, and each shipment ID can, and oftentimes, have multiple containers.
    Each shipment has a tracking page in the website, thus, performing operations must be done on the shipment's tracking page.
    The shipment class is initialized by providing a shipment ID, and a WebDriver instance of the full page.
    '''
    def __init__(self, shipment_id: str, page: WebDriver):
            
        self.page: WebDriver = page
        self.shipment_id: str = shipment_id
        self.containers: list[ContainerWithSiblings | ContainerWithNoSiblings] = self.get_containers()

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutError, TimeoutException), on_fail_message="Failed to get containers. Retrying...", on_fail_execute_message="Failed to get containers after 3 attempts")
    def get_containers(self) -> list[ContainerWithSiblings | ContainerWithNoSiblings]: 
        logging.info("Getting containers...")
        try:
            containers = WebDriverWait(self.page, TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, CONTAINER_CLASS_NAME))
            )
                
            logging.info(f"Found {len(containers)} containers.")
            
            return [ContainerWithSiblings(container) for container in containers]
            
        except TimeoutException as e:
            try:
                single_container = WebDriverWait(self.page, TIMEOUT).until(
                    EC.visibility_of_element_located((By.ID, SINGLE_CONTAINER_ID))
                )
                logging.info(f"Found 1 container.")
                return [ContainerWithNoSiblings(single_container, self.page)]
            except TimeoutException as e:
                raise ContainerNotFoundError(self.shipment_id, "get_containers", str(e))
        
        except Exception as e:
            raise ShipmentTimeoutError(self.shipment_id, "get_containers", str(e))

    
