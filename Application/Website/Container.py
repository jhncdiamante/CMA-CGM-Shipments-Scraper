from abc import abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.remote.webdriver import WebDriver

from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from .Milestone import Milestone
from selenium.common.exceptions import NoSuchElementException
from .Website import retry_until_success
import logging
import time
import random
from ..Log.logging_config import setup_logger
setup_logger()



TIMEOUT = 30

class Container:
    def __init__(self, container_element: WebElement, page: WebDriver):
        self.container_element = container_element
        self.container_page = page
        self.container_id = None
        self.milestones = None

    @abstractmethod
    def get_container_id(self) -> str:
        pass


    def display_previous_events(self) -> None:
        # Get the first result card
        button = WebDriverWait(self.container_element, TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[aria-label="Display Previous Moves"]'))
        )
        button.click()
        time.sleep(random.randint(5, 10))

    def get_milestones(self):
        def func():
            ref_rows = WebDriverWait(self.container_element, TIMEOUT).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.ico.ico-truck, .ico.ico-vessel')))
            rows = [row.find_element(By.XPATH, "../..") for row in ref_rows]

            return [Milestone(milestone_element) for milestone_element in rows]
        
        return retry_until_success(
            func=func,
            max_retries=3,
            delay=2,
            exceptions=(TimeoutError, TimeoutException),
            on_fail_message="Failed to get milestones. Retrying...",
            on_fail_execute_message="Failed to get milestones after 3 attempts"
        )



class ContainerWithSiblings(Container):
    '''
    The Container class represents a single container of a shipment. 
    Each container has a container ID, a expand button, a milestone panel, and a list of milestones.
    The container class is initialized by providing a container element and a WebDriver instance of the full page.
    The container class is responsible for extracting the container ID, expand button, milestone panel, and milestones.
    The container class is also responsible for clicking the expand button, and getting the milestone panel and milestones.
    Each container can, and oftentimes, have multiple milestones.
    '''
    def __init__(self, container_element: WebElement, page: WebDriver):
        super().__init__(container_element, page)
    
        self.container_id: str = self.get_container_id() # extract container ID
        self.display_details()
        self.display_previous_events()
        self.milestones = self.get_milestones()
        time.sleep(random.randint(5, 10))
        


    def display_details(self) -> None:
        def func():
            # Get the first result card
            button = WebDriverWait(self.container_element, TIMEOUT).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "section.result-card--actions"))
            )
            button.find_element(By.CSS_SELECTOR, "label").click()
       
        retry_until_success(
            func=func,
            max_retries=3,
            delay=2,
            exceptions=(TimeoutError, TimeoutException, ElementNotInteractableException),
            on_fail_message="Failed to display details. Retrying...",
            on_fail_execute_message="Failed to display details after 3 attempts")
    
    def get_container_id(self) -> str:
        def func():
            logging.info("Getting container ID...")
            container = WebDriverWait(self.container_element, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'section.result-card--content'))
            )
            container_id = container.find_element(By.XPATH, './/dl[@class="container-ref"]/dt/span[1]').text.strip()
            
            
            logging.info(f"Extracted Container ID: {container_id}")
                
            return container_id

        return retry_until_success(
            func=func,
            max_retries=3,
            delay=2,
            exceptions=(TimeoutError, TimeoutException),
            on_fail_message="Failed to get container ID. Retrying...",
            on_fail_execute_message="Failed to get container ID after 3 attempts"
        )
    

    


class ContainerWithNoSiblings(Container):
    def __init__(self, container_element: WebElement, page: WebDriver):
        super().__init__(container_element, page)
        self.container_id = self.get_container_id()
        
        self.display_previous_events()
        self.milestones = self.get_milestones()
        logging.info(f"No. of Milestones: {len(self.milestones)}")
        time.sleep(random.randint(5, 10))

    def get_container_id(self) -> str:
        def func():
            li_element = WebDriverWait(self.container_page, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//li[starts-with(normalize-space(text()), 'Container')]"))
            )
            container_id = li_element.find_element(By.TAG_NAME, "strong").text.strip()
            
            logging.info(f"Extracted Container ID: {container_id}")
            return container_id
        
        return retry_until_success(
            func=func,
            max_retries=3,
            delay=2,
            exceptions=(TimeoutError, TimeoutException, NoSuchElementException),
            on_fail_message="Failed to get container ID. Retrying...",
            on_fail_execute_message="Failed to get container ID after 3 attempts"
        )
    

    
