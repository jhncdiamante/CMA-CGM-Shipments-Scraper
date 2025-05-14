from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from .exceptions import ButtonNotFoundError

from ..Log.logging_config import setup_logger
setup_logger()

TIMEOUT = 180

class SearchBar:
    def __init__(self, driver):
        self._driver = driver # current page
        self.search_box = self.get_search_box(identifier=(By.ID, "Reference"))
        logging.info("Search box found.")
        self.search_button = self.get_search_button(identifier=(By.ID, "btnTracking"))
        logging.info("Search button found.")

    def get_search_button(self, identifier: tuple) -> WebElement:
        try:
            return WebDriverWait(self._driver, TIMEOUT).until(EC.element_to_be_clickable(identifier))
        except TimeoutException:
            logging.error("Failed to get search click button.")
            raise ButtonNotFoundError(identifier[1])

    def get_search_box(self, identifier: tuple) -> WebElement:
        try:
            # search box element is inside a shadow root
            search_box = WebDriverWait(self._driver, TIMEOUT).until(EC.visibility_of_element_located(identifier))
            # Access its shadow root
            return search_box
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Failed to access search bar. Error: {e}")
            raise NoSuchElementException(f"Failed to access search box with identifier: {identifier[1]}")

    def clear(self):
        self.search_box.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
        logging.info("Search box cleared.")

    def type_keyword(self, search_term):
        logging.info(f"Typing keyword: {search_term}")
        self.search_box.send_keys(search_term)
        logging.info(f"Keyword typed: {search_term}")

    def click_search_button(self):
        action = ActionChains(self._driver)
        logging.info("Clicking search button...")
        action.move_to_element(self.search_button).click().perform()
        logging.info("Search button clicked.")
