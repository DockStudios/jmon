
import abc
from typing import Optional

import dns.resolver


class StepState(abc.ABC):

    @abc.abstractmethod
    def __init__(self, response):
        """Store initial state"""
        ...

    @abc.abstractmethod
    def clone_to_child(self):
        """Clone current state to state for child step"""
        ...

    @abc.abstractmethod
    def integrate_from_child(self, child):
        """Integrate child state back into current state"""
        ...


class SeleniumStepState(StepState):

    def __init__(self, selenium_instance, element):
        self.element = element
        self.selenium_instance = selenium_instance

    def clone_to_child(self):
        """Clone current state to state for child step"""
        return SeleniumStepState(
            selenium_instance=self.selenium_instance,
            element=self.element
        )

    def integrate_from_child(self, child):
        """Integrate child state back into current state"""
        pass


class RequestsStepState(StepState):

    def __init__(self, response, dns_response: Optional['dns.resolver.Answer']):
        """Store state member variables"""
        self.response = response
        self.dns_response = dns_response

    def clone_to_child(self):
        """Clone current state to state for child step"""
        return RequestsStepState(
            response=self.response,
            dns_response=self.dns_response
        )

    def integrate_from_child(self, child: 'RequestsStepState'):
        """Integrate child state back into current state"""
        # Copy response back to parent object
        self.response = child.response
        self.dns_response = child.dns_response
