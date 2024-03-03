

from jmon.client_type import ClientType
from jmon.logger import logger
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.steps.base_step import BaseStep
from jmon.steps.dns_step import DNSStep
from jmon.steps.goto_step import GotoStep
from jmon.steps.find_step import FindStep
from jmon.steps.check_step import CheckStep
from jmon.steps.action_step import ActionStep
from jmon.steps.call_plugin_step import CallPluginStep


class RootStep(BaseStep):

    SHOULD_INFO_DEBUG_LOG = False

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME,
            ClientType.REQUESTS
        ]

    @property
    def supported_child_steps(self):
        """Return list of child support step classes"""
        return [
            GotoStep,
            FindStep,
            CheckStep,
            ActionStep,
            CallPluginStep,
            DNSStep,
        ]

    @property
    def id(self):
        """ID string for step"""
        return "Root"

    @property
    def description(self):
        """Friendly description of step"""
        return "Root step"

    def _validate_step(self):
        """Check step is valid"""
        pass

    def execute_requests(self, state: RequestsStepState):
        """Root module does nothing"""
        self._logger.debug(f"Starting root with config: {self._config}")

    def execute_selenium(self, state: SeleniumStepState):
        """Root module does nothing"""
        self._logger.debug(f"Starting root with config: {self._config}")
