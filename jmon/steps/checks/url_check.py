
import requests
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.checks.base_check import BaseCheck
from jmon.logger import logger
from jmon.utils import RetryStatus, retry


class UrlCheck(BaseCheck):
    """
    Directive for verifying current page URL.

    E.g.
    ```
    - goto: https://example.com
    - check:
        url: https://example.com/redirect-was-followed
    ```

    Variables provided by callable plugins can be used in the type value, e.g.
    ```
    - check:
        url: https://example.com/{an_output_variable}
    ```
    """

    CONFIG_KEY = "url"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.REQUESTS,
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME
        ]

    @property
    def id(self):
        """ID string for step"""
        return f"CheckUrl"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Check current URL of browser matches: {self.check_url}"

    @property
    def check_url(self):
        """Return URL to check"""
        return self.inject_variables_into_string(self._config)

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not str or not self._config:
            raise StepValidationError("Expected URL must be a valid string")

    @retry(count=5, interval=0.5)
    def _check_url(self, selenium_instance, url):
        """Check URL"""
        actual_url = selenium_instance.current_url
        if actual_url != url:
            self._logger.error(f'URL does not match excepted url. Expected "{url}" and got: {actual_url}')
            return None
        return True

    def execute_requests(self, state: RequestsStepState):
        """Check URL"""
        if self._check_valid_requests_response(state.response):
            return
        if state.response.url != self.check_url:
            self._logger.error(f'URL does not match excepted url. Expected "{self.check_url}" and got: {state.response.url}')
            self.set_status(StepStatus.FAILED)

    def execute_selenium(self, state: SeleniumStepState):
        """Check page URL"""
        res = self._check_url(state.selenium_instance, self.check_url, only_if=lambda: not self.has_timeout_been_reached())
        if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self.set_status(StepStatus.TIMEOUT)
        elif res is None:
            self.set_status(StepStatus.FAILED)
