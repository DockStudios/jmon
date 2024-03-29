
import selenium.common.exceptions

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.actions.base_action import BaseAction
from jmon.logger import logger
from jmon.utils import RetryStatus, retry


class TypeAction(BaseAction):
    """
    Directive for typing characters into the selected element.

    Supported keys:
     * `enter`

    E.g.
    ```
    - goto: https://example.com
    - find:
      - id: login
      - actions:
        - click
        - type: my-username
    ```

    Variables provided by callable plugins can be used in the type value, e.g.
    ```
    - actions:
      - type: '{an_output_variable}'
    ```
    """

    CONFIG_KEY = "type"

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
        return f"Type"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Typing text into browser element: {self.type_value}"

    @property
    def type_value(self):
        """Return text to type"""
        return self.inject_variables_into_string(self._config)

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not str or not self._config:
            raise StepValidationError(f"Text to type must be a string. Got: {self._config}")

    @retry(count=5, interval=0.5)
    def _type(self, element, text):
        try:
            element.send_keys(text)
            return True
        except selenium.common.exceptions.ElementNotInteractableException:
            return None

    def execute_selenium(self, state: SeleniumStepState):
        """Type text"""
        res = self._type(state.element, self.type_value, only_if=lambda: not self.has_timeout_been_reached())
        if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self.set_status(StepStatus.TIMEOUT)
        elif res is None:
            self.set_status(StepStatus.FAILED)
            self._logger.error("Unable to type into element")
