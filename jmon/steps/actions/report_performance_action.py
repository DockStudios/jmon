from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.steps.actions.base_action import BaseAction
from jmon.logger import logger
from jmon.step_status import StepStatus
from jmon.utils import RetryStatus, retry


class ReportPerformanceAction(BaseAction):
    """
    Directive for reporting performance

    E.g.
    ```
    - goto: https://example.com
    - actions:
      - report-performance
    ```

    This sets a "performance" run variable, which contains the following attributes:
      * pageSize
      * nrRequests
      * load
      * domContentLoaded
      * firstMeaningfulPaint
      * firstPaint
      * firstContentfulPaint

    These attributes can be used in plugins
    """

    CONFIG_KEY = "report-performance"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_CHROME
        ]

    def _validate_step(self):
        """Check step is valid"""
        if self._config is not None:
            raise StepValidationError(f"report-performance step should not have any attributes. Got: {self._config}")

    @property
    def id(self):
        """ID string for step"""
        return f"ReportPerformance"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Reporting Performance"

    @retry(count=1, interval=0)
    def _report_performance(self, selenium_instance):
        """Click mouse"""
        performance = selenium_instance.execute_script("tb:performance")
        self._run.set_variable("performance", performance)
        return True

    def execute_selenium(self, state: SeleniumStepState):
        """Perform"""
        res = self._report_performance(state.selenium_instance, only_if=lambda: not self.has_timeout_been_reached())
        if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self.set_status(StepStatus.TIMEOUT)

        if not res:
            self.set_status(StepStatus.FAILED)
