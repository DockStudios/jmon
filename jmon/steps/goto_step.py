
import json
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

    Variables provided by callable plugins can be used in the type value, e.g.
    ```
    - goto: https://example.com/?id={an_output_variable}
    ```

    For non-browser based tests, additional arguments can be provided to the Goto step:
    ```
    - goto:
        url: https://example.com/api/search
        headers:
          X-Api-Key: MyApiKey
        body: {'query': 'test'}
        method: POST
    ```
    Variables can also be used inside the header values, URL and body
    """

    CONFIG_KEY = "goto"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        if type(self._config) is str:
            # For goto steps that simply "goto" to a URL,
            # support all client types
            return [
                ClientType.BROWSER_FIREFOX,
                ClientType.BROWSER_CHROME,
                ClientType.REQUESTS
            ]

        # For checks that provide additional configs (method, body, headers),
        # only support requests
        return [
            ClientType.REQUESTS
        ]

    def __init__(self, run, config, parent, run_logger=None):
        """Calculate config"""
        super().__init__(run, config, parent, run_logger)
        self._method = "get"
        self._body = None
        self._headers = {}
        if type(self._config) is dict:
            self._method = self._config.get("method", "get").lower()
            self._json = self._config.get("body")
            self._headers = self._config.get("headers", {})

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is str:
            if not self._config:
                raise StepValidationError("Goto value must contain a value")
        elif type(self._config) is dict:
            # Ensure URL is provided
            if not self._config.get("url"):
                raise StepValidationError("Goto must contain a 'url' attribute")

            # Ensure method, if passed, is a valid method
            valid_methods = ["get", "post", "delete", "patch"]
            if self._config.get("method", "get").lower() not in valid_methods:
                raise StepValidationError(f"Goto method must be on of: {', '.join(valid_methods)}")

            # Ensure headers, if present, is a dict and contains only key values of strings
            if type(self._config.get("headers", {})) is not dict:
                raise StepValidationError("Goto headers must be an object with key-value headers")
            for header, value in self._config.get("headers", {}).items():
                if type(header) is not str or not header:
                    raise StepValidationError(f"Goto header '{header}' must be a string")
                if type(value) is not str or not value:
                    raise StepValidationError(f"Goto value for '{header}' must be a string")

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
        return f"Going to URL: {self.url}"

    @property
    def url(self):
        """Return URL"""
        url = self._config
        if type(self._config) is dict:
            url = self._config.get("url")
        return self.inject_variables_into_string(url)

    def execute_requests(self, state: RequestsStepState):
        """Execute step for requests"""
        request_kwargs = {
            "url": self.url,
            "headers": {
                key_: self.inject_variables_into_string(value_)
                for key_, value_ in self._headers.items()
            }
        }

        # Attempt to inject variables into body
        if self._body:
            try:
                json_encoded_body = json.dumps(self._body)
                json_encoded_body = self.inject_variables_into_string(json_encoded_body)
                self._body = json.loads(json_encoded_body)
            except ValueError:
                self._logger.warn("Failed to inject variables into body")

        # If body is a dictionary or list, send as json
        if type(self._body) in [list, dict]:
            request_kwargs["json"] = self._body
        else:
            request_kwargs["data"] = self._body

        # Get requests call method, based on provided method
        state.response = getattr(requests, self._method)(**request_kwargs)

    def execute_selenium(self, state: SeleniumStepState):
        """Goto URL"""
        try:
            state.selenium_instance.get(self.url)
        except selenium.common.exceptions.WebDriverException as exc:
            self.set_status(StepStatus.FAILED)
            self._logger.error(str(exc).split("\n")[0])
