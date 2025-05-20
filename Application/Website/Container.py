from abc import abstractmethod, ABC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from .Milestone import Milestone
from selenium.common.exceptions import NoSuchElementException

import logging
import time
import random
from ..Log.logging_config import setup_logger
setup_logger()
from .helpers import retryable 

# SuperClass Container 
DISPLAY_PREVIOUS_EVENTS_BUTTON = 'a[aria-label="Display Previous Moves"]'
REFERENCE_ROWS = '.ico.ico-truck, .ico.ico-vessel'
GRANDPARENT_ELEMENT = '../..'

# Container with siblings
ETA_ELEMENT = './/div[contains(text(), "ETA Berth at POD")]/..' 
CONTAINER_WS_ID_PANEL_CSS_SELECTOR = 'section.result-card--content'
CONTAINER_WS_ID_ELEMENT_XPATH = './/dl[@class="container-ref"]/dt/span[1]'
CONTAINER_WS_DETAILS_BUTTON_CSS_SELECTOR = "section.result-card--actions"


TIMEOUT = 30


class Container(ABC):
    def __init__(self, container_element: WebElement):
        self.container_element = container_element
        self.container_id: str = None
        self.milestones: list[Milestone] = None
        self.estimated_time_of_arrival: str = None

    @abstractmethod
    def get_estimated_time_of_arrival(self) -> str:
        pass

    @abstractmethod
    def get_container_id(self) -> str:
        pass

    @retryable(max_retries=3, delay=2, exceptions=(TimeoutError, TimeoutException), on_fail_message="Failed to display previous events. Retrying...", on_fail_execute_message="Failed to display previous events after 3 attempts")
    def display_previous_events(self) -> None:
        display_previous_events_button = WebDriverWait(self.container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, DISPLAY_PREVIOUS_EVENTS_BUTTON))
        )
        display_previous_events_button.click()
        time.sleep(random.randint(5, 10)) # wait for DOM changes


    @retryable(max_retries=3, delay=2, exceptions=(TimeoutError, TimeoutException), on_fail_message="Failed to get milestones. Retrying...", on_fail_execute_message="Failed to get milestones after 3 attempts")
    def get_milestones(self):
        # milestone elements have a complex hierarchy but
        # every event element has a sibling with span children containing truck or vessel icon
        # so we can use the truck or vessel icon to identify the event parent element(milestone row element)
        ref_rows = WebDriverWait(self.container_element, TIMEOUT).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, REFERENCE_ROWS)))
        
        rows = [row.find_element(By.XPATH, GRANDPARENT_ELEMENT) for row in ref_rows]
        
        logging.info(f"No. of Milestones: {len(rows)}")

        return [Milestone(milestone_element) for milestone_element in rows]
        


    def get_status(self, last_milestone: Milestone) -> bool:
        return last_milestone.event == "Gate out"



class ContainerWithSiblings(Container):
    '''
    The Container class represents a single container of a shipment. 
    Each container has a container ID, a expand button, a milestone panel, and a list of milestones.
    The container class is initialized by providing a container element and a WebDriver instance of the full page.
    The container class is responsible for extracting the container ID, expand button, milestone panel, and milestones.
    The container class is also responsible for clicking the expand button, and getting the milestone panel and milestones.
    Each container can, and oftentimes, have multiple milestones.
    '''
    def __init__(self, container_element: WebElement):
        super().__init__(container_element)
    
        self.container_id: str = self.get_container_id()
        self.display_details()
        self.display_previous_events()
        self.milestones = self.get_milestones()
        self.status = self.get_status(self.milestones[-1])
        self.eta = self.get_eta()
        time.sleep(random.randint(5, 10))

        
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutException, NoSuchElementException), on_fail_message="Failed to get eta. Retrying...", on_fail_execute_message="Failed to get eta after 3 attempts")
    def get_estimated_time_of_arrival(self) -> str:
        logging.info("Getting ETA...")
        eta_panel = WebDriverWait(self.container_element, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, ETA_ELEMENT))
        )
        date_spans = eta_panel.find_elements(By.TAG_NAME, "span")

        eta_info = " ".join([span.text.strip() for span in date_spans])
        logging.info(f"Extracted ETA: {eta_info}")
        return eta_info
       
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutError, TimeoutException, ElementNotInteractableException, NoSuchElementException), on_fail_message="Failed to display details. Retrying...", on_fail_execute_message="Failed to display details after 3 attempts")
    def display_details(self) -> None:
       
        button = WebDriverWait(self.container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, CONTAINER_WS_DETAILS_BUTTON_CSS_SELECTOR))
        )
        button.find_element(By.CSS_SELECTOR, "label").click()
    
    @retryable(max_retries=3, delay=2, exceptions=(TimeoutError, TimeoutException, NoSuchElementException), on_fail_message="Failed to get container ID. Retrying...", on_fail_execute_message="Failed to get container ID after 3 attempts")
    def get_container_id(self) -> str:
        logging.info("Getting container ID...")
        container_id_panel = WebDriverWait(self.container_element, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, CONTAINER_WS_ID_PANEL_CSS_SELECTOR))
        )
        container_id = container_id_panel.find_element(By.XPATH, CONTAINER_WS_ID_ELEMENT_XPATH).text.strip()
        
        logging.info(f"Extracted Container ID: {container_id}")
        return container_id

     

class ContainerWithNoSiblings(Container):
    def __init__(self, container_element: WebElement, page: WebDriver):
        super().__init__(container_element)
        self.container_page = page
        self.container_id = self.get_container_id()
        
        self.display_previous_events()
        self.milestones = self.get_milestones()
        
        self.status = self.get_status(self.milestones[-1])
        self.eta = self.get_eta()
        time.sleep(random.randint(5, 10))

    def get_estimated_time_of_arrival(self) -> str:
        try:
            return self.milestones[-1].date 
        except IndexError:
            raise IndexError("No milestones found for container with no siblings yet. Unable to get ETA.")


    @retryable(max_retries=3, delay=2, exceptions=(TimeoutError, TimeoutException, NoSuchElementException), on_fail_message="Failed to get container ID. Retrying...", on_fail_execute_message="Failed to get container ID after 3 attempts")
    def get_container_id(self) -> str:
      
        li_element = WebDriverWait(self.container_page, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//li[starts-with(normalize-space(text()), 'Container')]"))
        )
        container_id = li_element.find_element(By.TAG_NAME, "strong").text.strip()
        
        logging.info(f"Extracted Container ID: {container_id}")
        return container_id
        
      
    
