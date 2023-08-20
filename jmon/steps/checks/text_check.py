

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.checks.base_check import BaseCheck
from jmon.logger import logger
from jmon.utils import RetryStatus, retry


class TextCheck(BaseCheck):
    """
    Directive for verifying text content.

    E.g.
    ```
    - goto: https://example.com
    - check:
        text: "It's good"
    ```

    This directive can be used within a find element. E.g.:
    ```
    - goto: https://example.com
    - find:
      - id: login
      - check:
          text: Please Login
    ```
    """

    CONFIG_KEY = "text"

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
        return f"CheckText"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Check element text matches: {self._config}"

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not str or not self._config:
            raise StepValidationError("Expected text must be a valid string")

    @retry(count=5, interval=0.5)
    def _check_text(self, element, expected_title):
        """Check text"""
        actual_text = element.text
        if actual_text != expected_title:
            self._logger.error(f'Element text does not match excepted text. Expected "{self._config}" and got: "{actual_text}"')
            return None
        return True

    def execute_selenium(self, state: SeleniumStepState):
        """Check element text"""
        res = self._check_text(state.element, self._config, only_if=lambda: not self.has_timeout_been_reached())
        if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self.set_status(StepStatus.TIMEOUT)
        if res is None:
            self.set_status(StepStatus.FAILED)
