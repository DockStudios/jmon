
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
        message = "Check JSON response {}"
        if selector := self._config.get("selector", None):
            return f"Check JSON response matches: {self._config}"

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
            parser_message = f", from JSON selector '{parser.lpath}'"
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

