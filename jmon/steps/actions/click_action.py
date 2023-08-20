

import selenium.common.exceptions

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.steps.actions.base_action import BaseAction
from jmon.logger import logger
from jmon.step_status import StepStatus
from jmon.utils import RetryStatus, retry


class ClickAction(BaseAction):
    """
    Directive for clicking the current element, simulating a mouse left-click.

    E.g.
    ```
    - goto: https://example.com
    - find:
      - id: login
      - actions:
        - click
    ```
    """

    CONFIG_KEY = "click"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME
        ]

    def _validate_step(self):
        """Check step is valid"""
        if self._config is not None:
            raise StepValidationError(f"Click step should not have any attributes. Got: {self._config}")

    @property
    def id(self):
        """ID string for step"""
        return f"Click"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Clicking element"

    @retry(count=5, interval=0.5)
    def _click_element(self, element):
        """Click mouse"""
        try:
            element.click()
            return True
        except selenium.common.exceptions.ElementClickInterceptedException as exc:
            self._logger.error("Could not click on Element:")
            self._logger.debug(str(exc).split("\n")[0])
            return None

    def execute_selenium(self, state: SeleniumStepState):
        """Click mouse"""
        res = self._click_element(state.element, only_if=lambda: not self.has_timeout_been_reached())
        if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self.set_status(StepStatus.TIMEOUT)

        if not res:
            self.set_status(StepStatus.FAILED)
