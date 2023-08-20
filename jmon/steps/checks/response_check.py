

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState
from jmon.step_status import StepStatus
from jmon.steps.checks.base_check import BaseCheck


class ResponseCheck(BaseCheck):
    """
    Directive for verifying HTTP response code

    E.g.
    ```
    - goto: https://example.com
    - check:
        response: 200
    ```
    """

    CONFIG_KEY = "response"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.REQUESTS
        ]

    @property
    def id(self):
        """ID string for step"""
        return f"CheckResponseCode"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Check response code matches: {self._config}"

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not int:
            raise StepValidationError("Response code must be a number, e.g. 200")

    def execute_requests(self, state: RequestsStepState):
        """Check response code"""
        if self._check_valid_requests_response(state.response):
            return

        if state.response.status_code != self._config:
            self._logger.error(f"Expected status code: {self._config}, but got: {state.response.status_code}")
            self.set_status(StepStatus.FAILED)
