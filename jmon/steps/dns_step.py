
import json
import requests

import dns.rdatatype
import dns.resolver

from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.step_status import StepStatus
from jmon.steps.base_step import BaseStep
from jmon.logger import logger


class DNSStep(BaseStep):
    """
    Directive for checking a DNS response

    This should generally always be used as a first directive of a step.

    It can be used multiple times during a check.

    This can be placed in the root of the check, e.g.
    ```
    - dns: www.bbc.co.uk
    ```

    Variables provided by callable plugins can be used in the type value, e.g.
    ```
    - dns:
        domain: www.bbc.co.uk
        type: TXT
        name_servers:
         - 8.8.8.8
         - 1.1.1.1
        protocol: tcp
        lifetime: 2
        port: 53
        timeout: 5

    ```
    """

    CONFIG_KEY = "dns"

    DEFAULTS = {
        "timeout": 5,
        "lifetime": 1,
        "type": "a",
        "protocol": "udp",
        "port": 53,
    }

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        # Support all client types
        return [
            ClientType.REQUESTS
        ]

    def __init__(self, run, config, parent, run_logger=None):
        """Calculate config"""
        super().__init__(run, config, parent, run_logger)
        self._servers = []
        self._domain = None
        self._type = self.DEFAULTS["type"]
        self._lifetime = self.DEFAULTS["lifetime"]
        self._port = self.DEFAULTS["port"]
        self._protocol = self.DEFAULTS["protocol"]
        self._timeout = self.DEFAULTS["timeout"]

        if type(self._config) is str:
            self._domain = self._config

        if type(self._config) is dict:
            self._domain = self._config.get("domain")
            self._type = self._config.get("type", self.DEFAULTS["type"])
            self._servers = self._config.get("name_servers")
            self._protocol = self._config.get("protocol", self.DEFAULTS["protocol"]).lower()
            self._port = self._config.get("port", self.DEFAULTS["port"])
            self._lifetime = self._config.get("lifetime", self.DEFAULTS["lifetime"])
            self._timeout = self._config.get("timeout", self.DEFAULTS["timeout"])

        # Handle user passing a single server, rather than a list
        if type(self._servers) is str:
            self._servers = [self._servers]

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not dict and not self._domain:
            raise StepValidationError("DNS query domain must be specified as string to 'dns:' step")
        elif type(self._config) is dict and not self._domain:
            raise StepValidationError("DNS query domain must be specified in 'domain' field")

        if type(self._port) is not int:
            raise StepValidationError("DNS port must be a number")

        try:
            dns.rdatatype.from_text(self._type)
        except (dns.rdatatype.UnknownRdatatype, ValueError):
            raise StepValidationError("DNS query type must be a valid DNS query type, e.g. A, CNAME")


    @property
    def supported_child_steps(self):
        """Return list of child support step classes"""
        return []

    @property
    def id(self):
        """ID string for step"""
        return f"DNS"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Perform DNS query: {self._config}"

    def execute_requests(self, state: RequestsStepState):
        """Execute step for requests"""
        resolver = dns.resolver.Resolver()
        if self._servers:
            resolver.nameservers = self._servers
        resolver.port = self._port
        resolver.timeout = self._timeout
        kwargs = {
            "qname": self._domain,
            "rdtype": dns.rdatatype.from_text(self._type),
            "tcp": self._protocol.lower() == "tcp",
            "raise_on_no_answer": True,
            "lifetime": self._lifetime,
        }

        # Get requests call method, based on provided method
        try:
            state.dns_response = resolver.query(**kwargs)
        except Exception as exc:
            self.set_status(StepStatus.FAILED)
            self._logger.error(str(exc).split("\n")[0])
