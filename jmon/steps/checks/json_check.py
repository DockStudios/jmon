
from enum import Enum

from jsonpath import JSONPath

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState
from jmon.step_status import StepStatus
from jmon.steps.checks.base_check import BaseCheck


class JsonCheckMatchType(Enum):
    """Json value match types"""
    EQUALS = "equals"
    CONTAINS = "contains"


UNSET = object()


class JsonCheck(BaseCheck):
    """
    Directive for verifying the content of a JSON repsonse.

    One of two validation attributes must be used:
    * equals - Checks the value matches the provided content
    * contains - Checks that the provided value is within the content.

    A "selector" attribute may be provided to verify the value of a single element of the JSON response.
    The selector uses the syntax provided by [jsonpath](https://pypi.org/project/jsonpath-python).
    If a selector is not provided, the entire JSON response will be checked.

    ```
    - check:
        json:
          selector: '$.images[0]'
          contains: 1.jpg

    - check:
        json:
          selector: '$.id'
          equals: 1
    ```
    """

    CONFIG_KEY = "json"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.REQUESTS
        ]

    @property
    def id(self):
        """ID string for step"""
        return f"CheckJson"

    @property
    def description(self):
        """Friendly description of step"""
        parser, match_type, match_value = self._extract_selector_match_type()
        message = f"Check JSON response {match_type.value} {match_value}"

        if parser:
            message += f", using selector: {self._config.get('selector')}"

        return message

    def _extract_selector_match_type(self):
        """Return extractor and match type"""

        parsed_selector = None
        if selector := self._config.get("selector", None):
            try:
                parsed_selector = JSONPath(selector)
            except:
                raise StepValidationError(f"Invalid JSON selector selector: {selector}")

        equals_match = self._config.get(JsonCheckMatchType.EQUALS.value, UNSET)
        if equals_match != UNSET:
            return parsed_selector, JsonCheckMatchType.EQUALS, equals_match

        contains_match = self._config.get(JsonCheckMatchType.CONTAINS.value, UNSET)
        if contains_match != UNSET:
            return parsed_selector, JsonCheckMatchType.CONTAINS, contains_match

        return None, None, None

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not dict:
            raise StepValidationError(
                "json check must be a dictionary containing either 'contains' or 'equals'"
                " with an optional 'selector' attribute"
            )

        # Attempt to extract matchtor, which can raise an StepValidationError
        _, match_type, _ = self._extract_selector_match_type()
        if match_type is None:
            raise StepValidationError(
                "json check provider a comparator. Either 'contains' or 'equals'"
            )

    def _result_matches(self, state):
        """Determine if result is valid"""
        parser, match_type, match_value = self._extract_selector_match_type()

        actual_value = state.response.json()
        parser_message = ""
        if parser:
            actual_value = parser.parse(actual_value)
            parser_message = f", from JSON selector '{self._config.get('selector')}'"

            # Handle jsonpath return an array with single element when matching a single value
            if type(actual_value) is list and len(actual_value) == 1:
                actual_value = actual_value[0]

        if match_type is JsonCheckMatchType.EQUALS and match_value != actual_value:
            return False, f"Value '{actual_value}' does not match expected '{match_value}'{parser_message}"
        if match_type is JsonCheckMatchType.CONTAINS and match_value not in actual_value:
            return False, f"Could not find '{match_value}' in actual value '{actual_value}'{parser_message}"
        return True, None

    def execute_requests(self, state: RequestsStepState):
        """Check response code"""
        if self._check_valid_requests_response(state.response):
            return

        result, message = self._result_matches(state)
        if not result:
            self._set_status(StepStatus.FAILED)
            self._logger.error(f"JSON match failed: {message}\nFull Response: {state.response.json()}")

