
from typing import Any, Callable
import unittest.mock

import pytest
import dns.rdatatype
import dns.resolver

import jmon.step_status
import jmon.steps
import jmon.steps.checks
import jmon.errors
import jmon.client_type
import jmon.run_logger
from test.unit.jmon.steps.fixtures import mock_run, mock_logger, mock_root_step


@pytest.fixture
def get_dns_step(mock_run, mock_root_step, mock_logger) -> Callable[[Any], 'jmon.steps.DNSStep']:
    def inner(config):
        return jmon.steps.DNSStep(parent=mock_root_step, config=config, run=mock_run, run_logger=mock_logger)
    return inner


class TestDNSStep:

    @pytest.mark.parametrize('config', [
        # Test with string
        "www.example.com",

        {"domain": "www.example.com"},

        {"domain": "www.example.com", "name_servers": "1.1.1.1"},
        {"domain": "www.example.com", "name_servers": ["1.1.1.1"]},
        {"domain": "www.example.com", "type": "cname", "protocol": "tcp", "port": 52, "lifetime": 3, "timeout": 6},
    ])
    def test_create(self, config, mock_run, mock_root_step, mock_logger, get_dns_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test create with valid config"""
        step = get_dns_step(config)
        step.validate_steps()

    @pytest.mark.parametrize('config', [
        ["list"],
        {"without": "domain"},
        {"domain": "adg", "port": "astring"},
        {"domain": "adg", "type": "invalidtype"}
    ])
    def test_invalid_config(self, config, mock_run, mock_root_step, mock_logger, get_dns_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test create with valid config"""
        step = get_dns_step(config)
        with pytest.raises(jmon.errors.StepValidationError):
            step.validate_steps()

    @pytest.mark.parametrize('config, expected_resolver_config, expected_resolve_args', [
        ("www.example.com",
         {"nameservers": None, "port": 53, "timeout": 5},
         {"qname": 'www.example.com', "rdtype": dns.rdatatype.A, "tcp": False, "lifetime": 1}),
        ({"domain": "www.example.com"},
         {"nameservers": None, "port": 53, "timeout": 5},
         {"qname": 'www.example.com', "rdtype": dns.rdatatype.A, "tcp": False, "lifetime": 1}),
        # All args with nameserver list and TCP
        ({"domain": "www.full.example.com", "timeout": 76, "port": 51,
          "protocol": "tcp", "lifetime": 145, "type": "cname",
          "name_servers": ["1.5.2.3", "1.5.2.4"]},
         {"nameservers": ["1.5.2.3", "1.5.2.4"], "port": 51, "timeout": 76},
         {"qname": 'www.full.example.com', "rdtype": dns.rdatatype.CNAME, "tcp": True, "lifetime": 145}),

        # With UDP and nameserver string
        ({"domain": "www.full.example.com", "timeout": 76, "port": 51,
          "protocol": "udp", "lifetime": 145, "type": "mx",
          "name_servers": "1.3.2.3"},
         {"nameservers": ["1.3.2.3"], "port": 51, "timeout": 76},
         {"qname": 'www.full.example.com', "rdtype": dns.rdatatype.MX, "tcp": False, "lifetime": 145}),
    ])
    def test_execute_requests(self, config, expected_resolver_config, expected_resolve_args, mock_run, mock_root_step, mock_logger, get_dns_step: Callable[[Any], 'jmon.steps.DNSStep']):
        """Test DNS step"""
        class MockState:
            dns_response = None

        mock_state = MockState()

        step = get_dns_step(config)

        mock_dns_response = unittest.mock.MagicMock()
        class MockResolver:
            nameservers = None
            port = None
            timeout = None
            query = unittest.mock.MagicMock(return_value=mock_dns_response)
        mock_resolver = MockResolver()

        with unittest.mock.patch('dns.resolver.Resolver', unittest.mock.MagicMock(return_value=mock_resolver)):
            step.execute(execution_method='execute_requests', state=mock_state)

        assert step._status is jmon.step_status.StepStatus.SUCCESS

        MockResolver.query.assert_called_once_with(raise_on_no_answer=True, **expected_resolve_args)
        for k, v in expected_resolver_config.items():
            assert getattr(mock_resolver, k) == v

        assert mock_logger.read_log_stream() == ''
        assert mock_state.dns_response is mock_dns_response

    def test_execute_requests_exception(self, mock_run, mock_root_step, mock_logger, get_dns_step: Callable[[Any], 'jmon.steps.DNSStep']):
        """Test DNS step with resolution exception"""
        class MockState:
            dns_response = None

        mock_state = MockState()

        step = get_dns_step("adg.example.com")

        class MockResolver:
            nameservers = None
            port = None
            timeout = None
            query = unittest.mock.MagicMock(side_effect=dns.resolver.NXDOMAIN)
        mock_resolver = MockResolver()

        with unittest.mock.patch('dns.resolver.Resolver', unittest.mock.MagicMock(return_value=mock_resolver)):
            step.execute(execution_method='execute_requests', state=mock_state)

        assert step._status is jmon.step_status.StepStatus.FAILED

        assert mock_logger.read_log_stream() == '\n'.join([
            'Root -> DNS: Step failed',
            'Root -> DNS: The DNS query name does not exist.\n'
        ])
