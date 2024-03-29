

from pyvirtualdisplay import Display
import selenium
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import selenium.common.exceptions
import urllib3.exceptions
import psutil

from jmon.client_type import ClientType
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.actions.screenshot_action import ScreenshotAction
from jmon.config import ChromeHeadlessMode, Config
from jmon.logger import logger


class BrowserBase:
    """Base class for Browser management"""

    CLIENT_TYPE = None
    SELENIUM_CLASS = None

    @property
    def is_headless(self):
        """Return whether browser is running in headless mode"""
        raise NotImplementedError

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
        logger.info("Creating new browser")

        # Create selenium instance
        self._selenium_instance = self.selenium_class(**self.get_selenium_kwargs())

        # Maximise and setup implicit wait
        if self.is_headless:
            # If running in headless, set the window size directly
            # as maximise does not work
            self.selenium_instance.set_window_position(0, 0)
            self.selenium_instance.set_window_size(1920, 1080)
        else:
            # Otherwise, if using a read display, use maximum to
            # make use of the full display
            self.selenium_instance.maximize_window()
        self.selenium_instance.implicitly_wait(1)

        # Run post-setup configuration
        self._post_setup_configuration()

        # Obtain PID of browser
        self._pid = self.selenium_instance.service.process.pid

    def _post_setup_configuration(self):
        """Perform post-setup configuration"""
        raise NotImplementedError

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

        try:
            # Kill any selenium PIDs, if they exist
            psutil.Process(self._pid).terminate()
        # Catch error if PID doesn't exist due to browser
        # having close down correctly
        except psutil.Error:
            pass

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
        options = ChromeOptions()
        options.binary_location = "/opt/chrome-linux/chrome"
        options.add_argument('--no-sandbox')

        # Disable caching
        options.add_argument("--incognito")
        options.add_argument('--disable-application-cache')
        options.add_argument("--disk-cache-size=0")
        options.add_argument("--disk-cache-dir=/dev/null")

        # Set headles mode, if enabled
        if Config.get().CHROME_HEADLESS_MODE is not ChromeHeadlessMode.NONE:
            headless_argument = (
                "new"
                if Config.get().CHROME_HEADLESS_MODE is ChromeHeadlessMode.NEW else
                "chrome"
            )
            options.add_argument(f'--headless={headless_argument}')
        return {"chrome_options": options}

    @property
    def is_headless(self):
        """Return whether browser is running in headless mode"""
        return Config.get().CHROME_HEADLESS_MODE is not ChromeHeadlessMode.NONE

    def _post_setup_configuration(self):
        """Perform post-setup configuration"""
        # Disable network caching
        self.selenium_instance.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled":True})


class BrowserFirefox(BrowserBase):

    CLIENT_TYPE = ClientType.BROWSER_FIREFOX
    SELENIUM_CLASS = selenium.webdriver.Firefox

    def get_selenium_kwargs(self):
        """Return kwargs to pass to selenium"""
        options = FirefoxOptions()
        options.headless = Config.get().FIREFOX_HEADLESS

        # Create profile for disabling caching
        profile = FirefoxProfile()
        profile.set_preference('browser.cache.disk.enable', False)
        profile.set_preference('browser.cache.memory.enable', False)
        profile.set_preference('browser.cache.offline.enable', False)
        profile.set_preference('network.cookie.cookieBehavior', 2)
        profile.set_preference("browser.privatebrowsing.autostart", True)

        return {
            "options": options
        }

    @property
    def is_headless(self):
        """Return whether browser is running in headless mode"""
        return bool(Config.get().FIREFOX_HEADLESS)

    def _post_setup_configuration(self):
        """Perform post-setup configuration"""
        pass


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

                    logger.info("Using cached browser")
                    # Return the cached browser
                    return self._browser
                except Exception as exc:
                    logger.info("Error whilst cleaning cached browser: {exc}")
                    # Delete cached browser
                    self.teardown_browser()

            else:
                # Otherwise, if the cached browser type does not match
                # the required browser, tear it down
                logger.info("Browser type does not match cached browser - tearing down")
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

        run.logger.info(f"Supported clients: {', '.join([c.name for c in supported_clients])}")
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
                state=RequestsStepState(None, None)
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
                if not Config.get().CACHE_BROWSER:
                    logger.info("Tearing down browser - caching not enabled")
                    browser_factory.teardown_browser()

            except (selenium.common.exceptions.InvalidSessionIdException,
                    urllib3.exceptions.MaxRetryError,
                    selenium.common.exceptions.WebDriverException):
                # Handle Selenium invalid session ID
                # This implies that the browser has prematurely closed.
                # Or handle exceptions when unable to connect to selenium chromedriver
                # Silently retry the test
                browser_factory.teardown_browser()
                logger.info("Handling selenium-related exception - tearing down browser")
                raise

            except:
                browser_factory.teardown_browser()
                logger.info("Exception raised - tearing down browser")
                raise

        else:
            raise Exception(f"Unknown client: {client_type}")

        return status
