
from selenium.webdriver.common.keys import Keys
from jmon.client_type import ClientType
from jmon.step_status import StepStatus

from jmon.steps.actions.base_action import BaseAction
from jmon.logger import logger


class PressAction(BaseAction):

    CONFIG_KEY = "press"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX
        ]

    @property
    def id(self):
        """ID string for step"""
        return f"Press"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Pressing key: {self._config}"

    def execute_selenium(self, selenium_instance, element):
        """Press keyboard key"""
        if self._config.lower() == "enter":
            element.send_keys(Keys.ENTER)

        else:
            self._set_status(StepStatus.FAILED)
            self._logger.error(f'Unknown press action: {self._config}')

        return element
