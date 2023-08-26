

from pyvirtualdisplay import Display
import selenium
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions
import urllib3.exceptions

from jmon.client_type import ClientType
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.actions.screenshot_action import ScreenshotAction
from jmon.config import Config
from jmon.logger import logger


class BrowserBase:
    """Base class for Browser management"""

    CLIENT_TYPE = None
    SELENIUM_CLASS = None

    @property
    def selenium_class(self):
        """Return selenium type"""
        if self.SELENIUM_CLASS is None:
            raise NotImplementedError
        return self.SELENIUM_CLASS

    @property
    def client_type(self):
        """Return supported client type"""
        if self.CLIENT_TYPE is None:
            raise NotImplementedError

        return self.CLIENT_TYPE

    @property
    def selenium_instance(self):
        """Return selenium instance"""
        return self._selenium_instance

    def __init__(self):
        """Setup browser"""
        logger.debug("Creating new browser")

        # Create selenium instance
        self._selenium_instance = self.selenium_class(**self.get_selenium_kwargs())

        # Maximise and setup implicit wait
        self.selenium_instance.maximize_window()
        self.selenium_instance.implicitly_wait(1)

    def get_selenium_kwargs(self):
        """Return list of kwargs to provide to selenium"""
        raise NotImplementedError

    def teardown(self):
        """Teardown browser"""
        # Attempt to close browser
        try:
            self.selenium_instance.close()
        except (selenium.common.exceptions.InvalidSessionIdException,
                selenium.common.exceptions.WebDriverException,
                urllib3.exceptions.MaxRetryError) as exc:
            logger.error(str(exc))

        try:
            self.selenium_instance.quit()
        except urllib3.exceptions.MaxRetryError as exc:
            # Handle exceptions when unable to connect to selenium chromedriver
            logger.error(str(exc))

    def clean(self):
        """Clean browser between runs"""
        # Attempt to load blank page and delete cookies
        self.selenium_instance.get('about:blank')
        self.selenium_instance.delete_all_cookies()


class BrowserChrome(BrowserBase):

    CLIENT_TYPE = ClientType.BROWSER_CHROME
    SELENIUM_CLASS = selenium.webdriver.Chrome


    def get_selenium_kwargs(self):
        """Return kwargs to pass to selenium"""
        options = Options()
        options.binary_location = "/opt/chrome-linux/chrome"
        options.add_argument('--no-sandbox')
        return {"chrome_options": options}


class BrowserFirefox(BrowserBase):

    CLIENT_TYPE = ClientType.BROWSER_FIREFOX
    SELENIUM_CLASS = selenium.webdriver.Firefox

    def get_selenium_kwargs(self):
        """Return kwargs to pass to selenium"""
        return {}


class BrowserFactory:

    _INSTANCE = None

    @classmethod
    def get(cls):
        """Return instance of browser factory"""
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    @property
    def cached_browser_client_type(self):
        """Return client type of cached browser, if present"""
        if self._browser is not None:
            return self._browser.client_type
        return None

    def __init__(self):
        """Store member variable"""
        self._browser: BrowserBase = None
        self._class_mappings = {
            browser_class.CLIENT_TYPE: browser_class
            for browser_class in BrowserBase.__subclasses__()
        }

    def get_browser(self, client_type):
        """Obtain and cache browser"""
        # If a browser is already present
        if self._browser is not None:
            # If it matches the type, ensure it is working and return
            if client_type is self._browser.client_type:
                try:
                    self._browser.clean()

                    logger.debug("Using cached browser")
                    # Return the cached browser
                    return self._browser
                except Exception as exc:
                    logger.debug("Error whilst cleaning cached browser: {exc}")
                    # Delete cached browser
                    self.teardown_browser()

            else:
                # Otherwise, if the cached browser type does not match
                # the required browser, tear it down
                logger.debug("Browser type does not match cached browser - tearing down")
                self.teardown_browser()

        # If a cache browser has not been returned, create a new one
        self._browser = self.get_browser_class_by_client_type(client_type)()

        return self._browser

    def get_browser_class_by_client_type(self, client_type):
        """Return browser class by client type"""
        browser_class = self._class_mappings.get(client_type)
        if browser_class is None:
            raise Exception(f"Could not find browser class for client type: {client_type}")
        return browser_class

    def teardown_browser(self):
        """Tear down cached browser"""
        if self._browser:
            self._browser.teardown()
            self._browser = None


class Runner:
    """Execute run"""

    _DISPLAY = None

    @classmethod
    def get_display(cls):
        """Create display and cache"""
        if cls._DISPLAY is None:
            cls._DISPLAY = Display(visible=0, size=(1920, 1080))
            cls._DISPLAY.start()
        return cls._DISPLAY

    @classmethod
    def on_worker_startup(cls):
        """Handle worker startup"""
        cls.get_display()

    @classmethod
    def on_worker_shutdown(cls):
        """Hanle worker shutdown"""
        # Teardown any cached browsers
        BrowserFactory.get().teardown_browser()

        if cls._DISPLAY is not None:
            cls.get_display().stop()
            cls._DISPLAY = None

    def perform_check(self, run):
        """Setup selenium and perform checks"""
        supported_clients = run.check.get_supported_clients()

        run.logger.info(f"Supported clients: {supported_clients}")
        if not supported_clients:
            raise Exception("There are no supported clients for check")
        client_type = supported_clients[0]
        run.logger.info(f"Using client: {client_type}")

        # Default to failed status, assuming it will
        # be overriden by execution method
        status = StepStatus.FAILED

        if ClientType.REQUESTS in supported_clients:
            # Execute using requests
            run.start_timer()
            status = run.root_step.execute(
                execution_method='execute_requests',
                state=RequestsStepState(None)
            )
        elif ClientType.BROWSER_FIREFOX in supported_clients or ClientType.BROWSER_CHROME in supported_clients:

            browser_factory = BrowserFactory.get()

            # Check cached browser
            if ((cached_browser_client_type := browser_factory.cached_browser_client_type)
                    and cached_browser_client_type in supported_clients and
                    client_type is not cached_browser_client_type and
                    Config.get().PREFER_CACHED_BROWSER):

                run.logger.info(f"Switching run to cached browser: {cached_browser_client_type.value}")
                client_type = cached_browser_client_type

            # Ensure display is created
            self.get_display()

            try:
                browser = browser_factory.get_browser(client_type)
                selenium_instance = browser.selenium_instance

                root_state = SeleniumStepState(selenium_instance=selenium_instance, element=selenium_instance)

                # Start timeout timer once selenium has been initialised
                run.start_timer()

                status = run.root_step.execute(
                    execution_method='execute_selenium',
                    state=root_state
                )

                if status is StepStatus.FAILED and run.check.should_screenshot_on_error:
                    # Perform failure screenshot, if configured
                    error_screenshot = ScreenshotAction(
                        run=run,
                        config="failure",
                        parent=run.root_step,
                        run_logger=None
                    )
                    error_screenshot.execute(
                        execution_method='execute_selenium',
                        state=root_state
                    )

                # If any steps failed, clear browser
                if status is StepStatus.FAILED or not Config.get().CACHE_BROWSER:
                    browser_factory.teardown_browser()

            except (selenium.common.exceptions.InvalidSessionIdException,
                    urllib3.exceptions.MaxRetryError,
                    selenium.common.exceptions.WebDriverException):
                # Handle Selenium invalid session ID
                # This implies that the browser has prematurely closed.
                # Or handle exceptions when unable to connect to selenium chromedriver
                # Silently retry the test
                browser_factory.teardown_browser()
                raise

            except:
                browser_factory.teardown_browser()
                raise

        else:
            raise Exception(f"Unknown client: {client_type}")

        return status
