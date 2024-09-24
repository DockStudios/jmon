
from enum import Enum

import selenium.common.exceptions
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.wait

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.actions.base_action import BaseAction
from jmon.logger import logger
from jmon.utils import RetryStatus, retry


class WaitActionType(Enum):
    PRESENT   = "present"
    VISIBLE   = "visible"
    CLICKABLE = "clickable"


class WaitAction(BaseAction):
    """
    Directive for waiting for page readiness.

    Supported wait states:
     * `present` - Wait for element to be present on page
     * `visible` - Wait for element to be visible on screen
     * `clickable` - Wait for element to be clickable

    The default wait time is 60s.

    E.g.
    ```
    - goto: https://example.com
    - find:
      - id: login
      - actions:
        - wait: visible
    ```

    Specify custom timeout
    ```
    - actions:
       - wait:
           type: visible
           # Timeout in seconds
           timeout: 30
    ```
    """

    CONFIG_KEY = "wait"
    DEFAULT_TIMEOUT = 60

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
        return f"Wait"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Waiting for element - {self.get_wait_type().value}"

    def get_wait_type(self) -> WaitActionType:
        """Return text to type"""
        wait_type = None
        if type(self._config) is str:
            wait_type = self._config
        elif type(self._config) is dict:
            wait_type = self._config.get("type")
        else:
            raise StepValidationError(f"Wait type must be a string or an object with 'type' attribute. Got: {self._config}.{self.usage}")
        try:
            return WaitActionType(wait_type)
        except ValueError:
            raise StepValidationError(f"Wait type is invalid or not specified.{self.usage}")

    def get_timeout(self) -> int:
        """Get timeout"""
        timeout = self.DEFAULT_TIMEOUT
        if type(self._config) is dict and (config_timeout := self._config.get("timeout")):
            try:
                timeout = int(config_timeout)
            except:
                raise StepValidationError("Wait timeout is not a valid number")
        return timeout

    @property
    def usage(self) -> str:
        """Return usage information for step"""
        return """
e.g.
- actions:
  - wait: visible
or
- actions:
  - wait:
      type: visible
      # Timeout in seconds
      timeout: 30
"""

    def _validate_step(self):
        """Check step is valid"""
        # Validate wait type
        self.get_wait_type()
        # Validate timeout
        self.get_timeout()

    @retry(count=1, interval=0)
    def _wait(self, instance, element):
        """Perform wait"""
        until_method = None
        wait_type = self.get_wait_type()
        if wait_type is WaitActionType.PRESENT:
            until_method = EC.presence_of_element_located
        elif wait_type is WaitActionType.VISIBLE:
            until_method = EC.visibility_of
        elif wait_type is WaitActionType.CLICKABLE:
            until_method = EC.element_to_be_clickable
        else:
            raise Exception("Could not determine wait method for WatiActionType")

        try:
            selenium.webdriver.support.wait.WebDriverWait(instance, self.get_timeout()).until(until_method(element))
            return True
        except selenium.common.exceptions.TimeoutException:
            return None

    def execute_selenium(self, state: SeleniumStepState):
        """Perform wait"""
        res = self._wait(state.selenium_instance, state.element, only_if=lambda: not self.has_timeout_been_reached())
        if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self.set_status(StepStatus.TIMEOUT)
        elif res is None:
            self.set_status(StepStatus.FAILED)
            self._logger.error("Timeout ocurred before wait completed")
