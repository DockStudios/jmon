
import json
import requests
import selenium.common.exceptions
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState, SeleniumStepState

from jmon.step_status import StepStatus
from jmon.steps.base_step import BaseStep
from jmon.logger import logger
from jmon.utils import UNSET


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
        json: {'query': 'test'}
        method: POST
    - goto:
        url: https://example.com/api/search
        headers:
          X-Api-Key: MyApiKey
        body: "Some body string"
        method: PUT
    ```
    Variables can also be used inside the header values, URL and body
    """

    CONFIG_KEY = "goto"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        if type(self._config) is dict:
            # For checks that provide additional configs (method, body, headers),
            # only support requests
            return [
                ClientType.REQUESTS
            ]
        # Otherwise, for goto steps that simply "goto" to a URL,
        # support all client types
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME,
            ClientType.REQUESTS
        ]

    def __init__(self, run, config, parent, run_logger=None):
        """Calculate config"""
        super().__init__(run, config, parent, run_logger)
        self._method = "get"
        self._body = UNSET
        self._json = UNSET
        self._headers = {}
        if type(self._config) is dict:
            self._method = self._config.get("method", "get").lower()
            self._body = self._config.get("body", UNSET)
            self._json = self._config.get("json", UNSET)
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

            # Check remaining keys
            config_keys = [k for k in self._config.keys()]
            for valid_key in ["url", "method", "headers", "body"]:
                if valid_key in config_keys:
                    config_keys.remove(valid_key)
            if config_keys:
                raise StepValidationError(f"Found unsupported elements in Goto config: {', '.join(config_keys)}")
        else:
            raise StepValidationError(f"Goto value must be a URL or object with Goto attributes. Found type: {type(self._config)}")

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
        if self._json is not UNSET:
            def inject_variables_in_structure(structure):
                """Inject variables"""
                # If item is a string, replace value directly and return
                if type(structure) is str:
                    structure = self.inject_variables_into_string(structure)
                elif type(structure) is dict:
                    # Iterate through keys of a dict and replace each value
                    for key_, value_ in structure.items():
                        structure[key_] = inject_variables_in_structure(value_)
                elif type(structure) is list:
                    # Iterate through elements of lists and replace them with injected versions
                    for itx, val in enumerate(structure):
                        structure[itx] = inject_variables_in_structure(val)

                return structure
            self._json = inject_variables_in_structure(self._json)
            request_kwargs["json"] = self._json

        if self._body is not UNSET:
            self._body = self.inject_variables_into_string(self._body)
            request_kwargs["data"] = self._body

        # Get requests call method, based on provided method
        try:
            state.response = getattr(requests, self._method)(**request_kwargs)
        except Exception as exc:
            self.set_status(StepStatus.FAILED)
            self._logger.error(str(exc).split("\n")[0])

    def execute_selenium(self, state: SeleniumStepState):
        """Goto URL"""
        try:
            state.selenium_instance.get(self.url)
            state.element = state.selenium_instance
        except selenium.common.exceptions.WebDriverException as exc:
            self.set_status(StepStatus.FAILED)
            self._logger.error(str(exc).split("\n")[0])
