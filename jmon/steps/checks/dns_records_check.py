
from enum import Enum

from jsonpath import JSONPath

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState
from jmon.step_status import StepStatus
from jmon.steps.checks.base_check import BaseCheck


class DnsRecordsCheckMatchType(Enum):
    """DNS record value match types"""
    EQUALS = "equals"
    CONTAINS = "contains"
    COUNT = "count"
    MIN_COUNT = "min_count"


UNSET = object()


class DnsRecordsCheck(BaseCheck):
    """
    Directive for verifying the responses from DNS query.

    One of the following validation attributes must be used:
    * equals - Checks records match exactly
    * contains - Checks that the provided records exist in the response
    * count - Checks the number of records in the response
    * min_count - Checks the minimum number of records in the response

    ```
    - dns: www.google.co.uk
    - check:
        records:
          equals: 216.58.212.196

    - dns: www.bbc.co.uk
    - check:
        records:
          contains: [212.58.237.1, 212.58.235.1]

    # Ensure that at 3 records exist
    - dns: www.bbc.co.uk
    - check:
        records:
          count: 3

    # Ensure that at least 3 records exist
    - dns: www.bbc.co.uk
    - check:
        records:
          min_count: 3
    ```

    Variables provided by callable plugins can be used in the type value, e.g.
    ```
    - check:
        records:
          equals: '{an_output_variable}'
    ```
    """

    CONFIG_KEY = "records"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.REQUESTS
        ]

    @property
    def id(self):
        """ID string for step"""
        return f"CheckDNSRecords"

    @property
    def description(self):
        """Friendly description of step"""
        match_type, match_value = self._extract_selector_match_type()
        message = f"Check DNS records {match_type.value} {match_value}"

        return message

    def _extract_selector_match_type(self):
        """Return extractor and match type"""
        equal_value = self._config.get(DnsRecordsCheckMatchType.EQUALS.value, UNSET)
        if equal_value != UNSET:
            # If a single record was supplied, convert to list
            if type(equal_value) is str:
                equal_value = [equal_value]

            return DnsRecordsCheckMatchType.EQUALS, equal_value

        contains_value = self._config.get(DnsRecordsCheckMatchType.CONTAINS.value, UNSET)
        if contains_value != UNSET:
            # If a single record was supplied, convert to list
            if type(contains_value) is str:
                contains_value = [contains_value]

            return DnsRecordsCheckMatchType.CONTAINS, contains_value

        count = self._config.get(DnsRecordsCheckMatchType.COUNT.value, UNSET)
        if count != UNSET:
            return DnsRecordsCheckMatchType.COUNT, count

        count_min = self._config.get(DnsRecordsCheckMatchType.MIN_COUNT.value, UNSET)
        if count_min != UNSET:
            return DnsRecordsCheckMatchType.MIN_COUNT, count_min

        return None, None

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not dict:
            raise StepValidationError(
                "DNS response check must be a dictionary containing either 'contains', 'equals', 'count' or 'min_count'"
            )

        # Attempt to extract matchtor, which can raise an StepValidationError
        match_type, _ = self._extract_selector_match_type()
        if match_type is None:
            raise StepValidationError(
                "DNS response check provider a comparator. Either 'contains', 'equals', 'count' or 'min_count'"
            )

    def _result_matches(self, state: RequestsStepState):
        """Determine if result is valid"""
        match_type, match_value = self._extract_selector_match_type()

        actual_value = [
            ip.address
            for ip in state.dns_response.rrset
        ]

        # If compare value is a string, inject variables
        match_value = self.inject_variables_into_string(match_value)

        if match_type is DnsRecordsCheckMatchType.EQUALS and match_value.sort() != actual_value.sort():
            return False, f"Value '{', '.join(actual_value)}' does not match expected '{','.join(match_value)}'"
        if match_type is DnsRecordsCheckMatchType.CONTAINS:
            not_found = [
                ip_itx
                for ip_itx in match_value
                if ip_itx not in actual_value
            ]
            if not_found:
                return False, f"Could not find IPs '{', '.join(not_found)}' in actual value '{','.join(actual_value)}'"
        if match_type is DnsRecordsCheckMatchType.COUNT:
            if len(actual_value) != match_value:
                return False, f"Number of records is not {match_value}: {', '.join(actual_value)}"
        if match_type is DnsRecordsCheckMatchType.MIN_COUNT:
            if len(actual_value) < match_value:
                return False, f"Number of records is less than {match_value}: {', '.join(actual_value)}"
        return True, None

    def execute_requests(self, state: RequestsStepState):
        """Check response code"""
        if self._check_valid_dns_response(state.dns_response):
            return

        result, message = self._result_matches(state)
        if not result:
            self.set_status(StepStatus.FAILED)
            self._logger.error(f"DNS records match failed: {message}")
