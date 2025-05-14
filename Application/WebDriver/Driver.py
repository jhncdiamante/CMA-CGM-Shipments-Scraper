import undetected_chromedriver as uc

from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging


# Configure logging
logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode='w'  # Clear the file on each run
)

TIMEOUT = 60
class Driver:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.chrome_options = Options()
        self.ua = UserAgent()
        self.setUpDriver()
        self.wait = WebDriverWait(self.driver, TIMEOUT, poll_frequency=0.5)

    def setUpDriver(self):
        logging.info("Setting up driver...")
        if self.headless:
           self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--disable-gpu")

        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--ignore-ssl-errors=yes")

        self.chrome_options.add_argument(
            "--disable-web-security"
        )  # Disable web security policies
        self.chrome_options.add_argument(
            "--allow-running-insecure-content"
        )  # Allow mixed content
        self.chrome_options.add_argument("--log-level=3")  # Minimize browser log output
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--enable-unsafe-swiftshader")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-browser-side-navigation")
        self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        self.chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-infobars")
        # Initialize the WebDriver
        self.driver = uc.Chrome(
            version_main=135, options=self.chrome_options, use_subprocess=True
        )
        '''
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {"userAgent": self.ua.random},  # Pass the User-Agent as a dictionary
        )'''

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
            },
        )

   