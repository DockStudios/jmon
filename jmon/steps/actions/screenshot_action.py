
import os
import re
from selenium.webdriver.common.keys import Keys
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState

from jmon.steps.actions.base_action import BaseAction
from jmon.logger import logger


class ScreenshotAction(BaseAction):
    """
    Directive for capturing a screenshot of the current page.

    A value must be provided, which will be the name given to the screenshot.

    This action can be performed multiple times.

    E.g.
    ```
    - goto: https://example.com
    - actions:
      - screenshot: example
    - goto: https://example.com/login
    - actions:
      - screenshot: example-login
    ```
    """

    CONFIG_KEY = "screenshot"
    NAME_REGEX = re.compile(r'[^\w^_^-]')
    TEMP_DIRECTORY = '/tmp'

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME
        ]

    @property
    def id(self):
        """ID string for step"""
        return f"Screenshot"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Taking screenshot of browser: {self.screenshot_file_name}"

    @property
    def screenshot_file_name(self):
        """Return name of screenshot file"""
        # Handle None screenshot name
        screenshot_name = self._config or ''

        # Remove any special characters from screenshot
        screenshot_name = self.NAME_REGEX.sub('', screenshot_name)

        if not screenshot_name:
            raise Exception('Screenshot name is invalid')

        return f"{screenshot_name}.png"

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not str or not self._config:
            raise StepValidationError(f"Screenshot name must be provided. Got: {self._config}")

    def execute_selenium(self, state: SeleniumStepState):
        """Press keyboard key"""
        screenshot_path = os.path.join(self.TEMP_DIRECTORY, self.screenshot_file_name)

        state.selenium_instance.save_screenshot(screenshot_path)

        self._run.register_artifact(screenshot_path)
