
from time import sleep

from pyvirtualdisplay import Display
import selenium
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions

from jmon.client_type import ClientType
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.actions.screenshot_action import ScreenshotAction


class Runner:
    """Execute run"""

    DISPLAY = None

    @staticmethod
    def get_display():
        if Runner.DISPLAY is None:
            Runner.DISPLAY = Display(visible=0, size=(1920, 1080))
            Runner.DISPLAY.start()
        return Runner.DISPLAY

    @staticmethod
    def get_selenium_instance(client_type):
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

        # Get display
        Runner.get_display()

        selenium_instance = browser_class(**kwargs)
        selenium_instance.maximize_window()
        selenium_instance.implicitly_wait(1)

        # Remove cookies before starting
        selenium_instance.get('about:blank')
        selenium_instance.delete_all_cookies()

        return selenium_instance

    def stop_selemium(self, selenium_instance):
        """Quit selenium and remove all child processes"""
        selenium_instance.close()
        selenium_instance.quit()

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

        if client_type is ClientType.REQUESTS:
            # Execute using requests
            run.start_timer()
            status = run.root_step.execute(
                execution_method='execute_requests',
                state=RequestsStepState(None)
            )
        elif client_type in [ClientType.BROWSER_FIREFOX, ClientType.BROWSER_CHROME]:

            selenium_instance = self.get_selenium_instance(client_type)

            root_state = SeleniumStepState(selenium_instance=selenium_instance, element=selenium_instance)

            # Start timeout timer once selenium has been initialised
            run.start_timer()

            try:
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

            finally:
                self.stop_selemium(selenium_instance)

        else:
            raise Exception(f"Unknown client: {client_type}")

        return status
