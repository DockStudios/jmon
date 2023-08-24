

from pyvirtualdisplay import Display
import selenium
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions

from jmon.client_type import ClientType
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.actions.screenshot_action import ScreenshotAction
from jmon.config import Config
from jmon.logger import logger


class Runner:
    """Execute run"""

    _DISPLAY = None
    _SELENIUM_INSTANCE = None
    _SELENIUM_INSTANCE_TYPE = None

    @classmethod
    def get_browser(cls, client_type):
        """Obtain and cache browser"""

        # If a browser is already present
        if cls._SELENIUM_INSTANCE is not None:
            # If it matches the type, ensure it is working and return
            if client_type is cls._SELENIUM_INSTANCE_TYPE:
                selenium_instance = cls._SELENIUM_INSTANCE
                try:
                    # Attempt to load blank page and delete cookies
                    selenium_instance.get('about:blank')
                    selenium_instance.delete_all_cookies()

                    logger.debug("Using cached browser")
                    # Return the cached browser
                    return selenium_instance
                except:
                    logger.debug("Error whilst cleaning cached browser")
                    # Delete cached browser
                    cls.teardown_browser()

            else:
                # Otherwise, if the cached browser type does not match
                # the required browser, tear it down
                logger.debug("Browser type does not match cached browser - tearing down")
                cls.teardown_browser()

        # If a cache browser has not been returned, create a new one
        logger.debug("Creating new browser")
        kwargs = {}
        browser_class = None

        if client_type is ClientType.BROWSER_FIREFOX:
            browser_class = selenium.webdriver.Firefox
        elif client_type is ClientType.BROWSER_CHROME:
            browser_class = selenium.webdriver.Chrome
            options = Options()
            options.binary_location = "/opt/chrome-linux/chrome"
            options.add_argument('--no-sandbox')
            kwargs["chrome_options"] = options
        else:
            raise Exception(f"Unrecognised selenium ClientType: {client_type}")


        # Create selenium instance
        selenium_instance = browser_class(**kwargs)

        # Maximise and setup implicit wait
        selenium_instance.maximize_window()
        selenium_instance.implicitly_wait(1)

        # Cache browser type
        cls._SELENIUM_INSTANCE = selenium_instance
        cls._SELENIUM_INSTANCE_TYPE = client_type

        return selenium_instance

    @classmethod
    def teardown_browser(cls):
        """Tear down selenium instance"""
        if cls._SELENIUM_INSTANCE:
            logger.debug("Tearing down browser")
            cls._SELENIUM_INSTANCE.close()
            cls._SELENIUM_INSTANCE.quit()
            cls._SELENIUM_INSTANCE = None
            cls._SELENIUM_INSTANCE_TYPE = None

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
        cls.teardown_browser()

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

            # Check cached browser
            if (self._SELENIUM_INSTANCE_TYPE is not None
                    and self._SELENIUM_INSTANCE_TYPE in supported_clients and
                    client_type is not self._SELENIUM_INSTANCE_TYPE):

                run.logger.info(f"Cached browser is {self._SELENIUM_INSTANCE_TYPE}, switching run to this")
                client_type = self._SELENIUM_INSTANCE_TYPE

            # Ensure display is created
            self.get_display()

            try:
                selenium_instance = self.get_browser(client_type)

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
                    self.teardown_browser()

            except selenium.common.exceptions.InvalidSessionIdException:
                # Handle Selenium invalid session ID
                # This implies that the browser has prematurely closed
                # Silently retry the test
                if self._SELENIUM_INSTANCE:
                    self._SELENIUM_INSTANCE.quit()
                    self._SELENIUM_INSTANCE = None
                    self._SELENIUM_INSTANCE_TYPE = None
                raise

            except:
                self.teardown_browser()
                raise

        else:
            raise Exception(f"Unknown client: {client_type}")

        return status
