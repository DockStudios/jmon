
import requests
import selenium.common.exceptions
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState, SeleniumStepState

from jmon.step_status import StepStatus
from jmon.steps.base_step import BaseStep
from jmon.logger import logger


class GotoStep(BaseStep):
    """
    Directive for loading a page.

    This should generally always be used as a first directive of a step.

    It can be used multiple times during a check.

    This can be placed in the root of the check, e.g.
    ```
     - goto: https://example.com
     - find:
       - tag: input
       - url: https://example.com/?followed=redirect

     - goto: https://example.com/login
    ```
    """

    CONFIG_KEY = "goto"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME,
            ClientType.REQUESTS
        ]

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not str or not self._config:
            raise StepValidationError("Goto value must be a URL")

    @property
    def supported_child_steps(self):
        """Return list of child support step classes"""
        return []

    @property
    def id(self):
        """ID string for step"""
        return f"GoTo"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Going to URL: {self._config}"

    def execute_requests(self, state: RequestsStepState):
        """Execute step for requests"""
        state.response = requests.get(self._config)

    def execute_selenium(self, state: SeleniumStepState):
        """Goto URL"""
        try:
            state.selenium_instance.get(self._config)
        except selenium.common.exceptions.WebDriverException as exc:
            self._set_status(StepStatus.FAILED)
            self._logger.error(str(exc).split("\n")[0])
