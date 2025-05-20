from abc import ABC
from Application.WebDriver.Driver import Driver
import logging

from ..Log.logging_config import setup_logger
setup_logger()

class Website(ABC):
    def __init__(self, base_url):
        self._driver_instance = Driver(headless=False)
        self._driver = self._driver_instance.driver
        self._wait = self._driver_instance.wait
        self._base_url = base_url

    def open_page(self, url):
        self._driver.get(url)
        logging.info(f"Opening page: {url}")    
        self._wait.until(
            lambda _: self._driver.execute_script('return document.readyState') == 'complete'
        )
        logging.info(f"Page loaded: {url}")

