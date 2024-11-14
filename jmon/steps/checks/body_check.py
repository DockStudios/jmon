
from enum import Enum

import requests.exceptions
from jsonpath import JSONPath

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.checks.base_check import BaseCheck
from jmon.utils import RetryStatus, retry


class BodyCheckMatchType(Enum):
    """Body value match types"""
    EQUALS = "equals"
    CONTAINS = "contains"


UNSET = object()


class BodyCheck(BaseCheck):
    """
    Directive for verifying the content of the repsonse body.

    One of two validation attributes must be used:
    * equals - Checks the value matches the provided content
    * contains - Checks that the provided value is within the content.

    ```
    - check:
        body:
          contains: 'Some Text'

    - check:
        body:
          equals: 'Some text'
    ```

    Variables provided by callable plugins can be used in the type value, e.g.
    ```
    - check:
        body:
          equals: '{an_output_variable}'
    ```
    """

    CONFIG_KEY = "body"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            # ClientType.BROWSER_FIREFOX,
            # ClientType.BROWSER_CHROME,
            ClientType.REQUESTS,
        ]

    @property
    def id(self):
        """ID string for step"""
        return f"CheckBody"

    @property
    def description(self):
        """Friendly description of step"""
        match_type, match_value = self._extract_selector_match_type()
        return f"Check page body {match_type.value} {match_value}"

    def _extract_selector_match_type(self):
        """Return extractor and match type"""
        equals_match = self._config.get(BodyCheckMatchType.EQUALS.value, UNSET)
        if equals_match != UNSET:
            return BodyCheckMatchType.EQUALS, equals_match

        contains_match = self._config.get(BodyCheckMatchType.CONTAINS.value, UNSET)
        if contains_match != UNSET:
            return BodyCheckMatchType.CONTAINS, contains_match

        return None, None

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not dict:
            raise StepValidationError(
                "json check must be a dictionary containing either 'contains' or 'equals'"
                " with an optional 'selector' attribute"
            )

        # Attempt to extract matchtor, which can raise an StepValidationError
        match_type, _ = self._extract_selector_match_type()
        if match_type is None:
            raise StepValidationError(
                "body check must contain a comparator. Either 'contains' or 'equals'"
            )

    def _result_matches(self, body: str):
        """Determine if result is valid"""
        match_type, match_value = self._extract_selector_match_type()

        parser_message = f"\nFull body: {body}"

        # If compare value is a string, inject variables
        # @TODO How can we handle injecting variables to lists/dicts
        match_value = self.inject_variables_into_string(match_value)

        if match_type is BodyCheckMatchType.EQUALS and match_value != body:
            return False, f"Body does not match expected '{match_value}'{parser_message}"
        if match_type is BodyCheckMatchType.CONTAINS and match_value not in body:
            return False, f"Could not find '{match_value}' in body{parser_message}"
        return True, None

    # @retry(count=5, interval=0.5)
    # def _check_selenium(self, state: SeleniumStepState):
    #     """Check body"""
    #     result, message = self._result_matches(state.selenium_instance.page_source)
    #     if not result:
    #         self._logger.error(message)
    #         return None
    #     return True

    # def execute_selenium(self, state: SeleniumStepState):
    #     """Execution wrapper for selenium"""
    #     res = self._check_selenium(state, only_if=lambda: not self.has_timeout_been_reached())
    #     if res is RetryStatus.ONLY_IF_CONDITION_FAILURE:
    #         self.set_status(StepStatus.TIMEOUT)
    #     if res is None:
    #         self.set_status(StepStatus.FAILED)

    def execute_requests(self, state: RequestsStepState):
        """Execution wrapper for requests"""
        if self._check_valid_requests_response(state.response):
            return

        result, message = self._result_matches(state.response.content)
        if not result:
            self.set_status(StepStatus.FAILED)
            self._logger.error(f"body match failed: {message}")

