
from selenium.webdriver.common.keys import Keys
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.step_status import StepStatus

from jmon.steps.actions.base_action import BaseAction
from jmon.logger import logger


class PressAction(BaseAction):
    """
    Directive for pressing buttons, simulating a keyboard button press.

    Supported keys:
     * `enter`

    E.g.
    ```
    - goto: https://example.com
    - find:
      - id: login
      - actions:
        - press: enter
    ```
    """

    CONFIG_KEY = "press"

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
        return f"Press"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Pressing key: {self._config}"

    def _validate_step(self):
        """Check step is valid"""
        if self._config not in ["enter"]:
            raise StepValidationError(f"Press supports the following keys: enter. Got value: {self._config}")


    def execute_selenium(self, state: SeleniumStepState):
        """Press keyboard key"""
        if self._config.lower() == "enter":
            state.element.send_keys(Keys.ENTER)

        else:
            self._set_status(StepStatus.FAILED)
            self._logger.error(f'Unknown press action: {self._config}')
