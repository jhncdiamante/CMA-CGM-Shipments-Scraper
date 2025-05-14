from abc import ABC
from Application.WebDriver.Driver import Driver
import time
from selenium.webdriver.support.ui import WebDriverWait
import logging

from ..Log.logging_config import setup_logger
setup_logger()


def retry_until_success(func, max_retries, delay=2, exceptions=(Exception,), on_fail_message=None, on_fail_execute_message=None):
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            logging.info(f"{on_fail_message or 'Attempt failed'}, retrying... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
    raise Exception(on_fail_execute_message or "Max retries exceeded")


class Website(ABC):
    def __init__(self, base_url):
        self.DriverInstance = Driver(headless=False)
        self._driver = self.DriverInstance.driver
        self._wait = self.DriverInstance.wait
        self._base_url = base_url

    def open_page(self, url):
        self._driver.get(url)
        logging.info(f"Opening page: {url}")    
        self._wait.until(
            lambda _: self._driver.execute_script('return document.readyState') == 'complete'
        )
        logging.info(f"Page loaded: {url}")

