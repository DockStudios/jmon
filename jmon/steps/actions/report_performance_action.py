from typing import Any, Optional, Dict
import dataclasses

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.steps.actions.base_action import BaseAction
from jmon.logger import logger
from jmon.step_status import StepStatus
from jmon.utils import RetryStatus, retry


@dataclasses.dataclass
class PerformanceData:

    load: int
    dom_content_loaded: int
    interactive: int

    @classmethod
    def from_performance_output(cls, performance_output: Dict[str, Any]) -> Optional['PerformanceData']:
        """Generate performance data from output"""
        if not isinstance(performance_output, dict):
            return None

        origin = performance_output.get("timeOrigin")
        if not origin:
            return None

        timing = performance_output.get("timing", {})
        if not isinstance(timing, dict):
            return None

        load_time_end = timing.get("loadEventEnd")
        load_time = 0
        if isinstance(load_time_end, int):
            load_time = load_time_end - origin

        interactive_time_end = timing.get("domInteractive")
        if isinstance(load_time_end, int):
            interactive_time = interactive_time_end - origin

        dom_content_loaded_end = timing.get("domContentLoadedEventEnd")
        dom_content_loaded = 0
        if isinstance(dom_content_loaded_end, int):
            dom_content_loaded = dom_content_loaded_end - origin

        return cls(
            load=load_time,
            interactive=interactive_time,
            dom_content_loaded=dom_content_loaded,
        )


class ReportPerformanceAction(BaseAction):
    """
    Directive for reporting performance

    E.g.
    ```
    - goto: https://example.com
    - actions:
      - report-performance
    ```

    This sets a "performance" run variable, which contains an instance of PerformanceData with the following attributes:
      * load
      * dom_content_loaded
      * interactive

    This object can be used in plugins.
    """

    CONFIG_KEY = "report-performance"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
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
        """Run performance report"""
        performance_data = selenium_instance.execute_script("return performance;")
        self._run.set_variable("performance", PerformanceData.from_performance_output(performance_data))
        return True

    def execute_selenium(self, state: SeleniumStepState):
        """Perform"""
        res = self._report_performance(state.selenium_instance, only_if=lambda: not self.has_timeout_been_reached())
        if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self.set_status(StepStatus.TIMEOUT)

        if not res:
            self.set_status(StepStatus.FAILED)
