

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.checks.base_check import BaseCheck
from jmon.logger import logger
from jmon.utils import RetryStatus, retry


class TitleCheck(BaseCheck):
    """
    Directive for verifying HTML page title.

    E.g.
    ```
    - goto: https://example.com
    - check:
        title: "Example - Homepage"
    ```
    """

    CONFIG_KEY = "title"

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
        return f"CheckTitle"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Check current title of browser matches: {self._config}"

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not str or not self._config:
            raise StepValidationError("Expected title must be a valid string")

    @retry(count=5, interval=0.5)
    def _check_title(self, selenium_instance, expected_title):
        """Check title"""
        actual_title = selenium_instance.title
        if actual_title != expected_title:
            self._logger.error(f'Title does not match excepted title. Expected "{self._config}" and got: "{actual_title}"')
            return None
        return True

    def execute_selenium(self, state: SeleniumStepState):
        """Check page title"""
        res = self._check_title(state.selenium_instance, self._config, only_if=lambda: not self.has_timeout_been_reached())
        if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self._set_status(StepStatus.TIMEOUT)
        elif res is None:
            self._set_status(StepStatus.FAILED)
