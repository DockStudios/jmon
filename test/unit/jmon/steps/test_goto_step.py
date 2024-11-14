
from typing import Any, Callable
import unittest.mock

import pytest
import requests.exceptions
import selenium.common.exceptions

import jmon.step_status
import jmon.steps
import jmon.steps.checks
import jmon.errors
import jmon.client_type
import jmon.run_logger
from test.unit.jmon.steps.fixtures import mock_run, mock_logger, mock_root_step


@pytest.fixture
def get_goto_step(mock_run, mock_root_step, mock_logger) -> Callable[[Any], 'jmon.steps.GotoStep']:
    def inner(config):
        return jmon.steps.GotoStep(parent=mock_root_step, config=config, run=mock_run, run_logger=mock_logger)
    return inner


class TestGotoStep:

    @pytest.mark.parametrize('config', [
        # Just URL
        "https://example.com/someurl",

        {"url": "https://example.com/someurl"},
        # With methods
        {"url": "https://example.com/someurl", "headers": {"some-header": "headervalue"}, "body": "somebody", "method": "get"},
        {"url": "https://example.com/someurl", "headers": {"some-header": "headervalue"}, "body": "somebody", "method": "post"},
        {"url": "https://example.com/someurl", "headers": {"some-header": "headervalue"}, "body": "somebody", "method": "delete"},
        {"url": "https://example.com/someurl", "headers": {"some-header": "headervalue"}, "body": "somebody", "method": "patch"},

        # With timeout
        {"url": "https://example.com/someurl", "headers": {"some-header": "headervalue"}, "timeout": 5},
    ])
    def test_create(self, config, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test create with valid config"""
        step = get_goto_step(config)
        step.validate_steps()

    @pytest.mark.parametrize('config', [
        # List value,
        ['Test Value'],

        # Dict without URL
        {'something_else': 'value'},

        # Invalid method
        {"url": "https://example.com/someurl", "method": "wrong"},
        # Invalid headers type
        {"url": "https://example.com/someurl", "headers": "string"},
        {"url": "https://example.com/someurl", "headers": ["list"]},

        # Invalid timeout value
        {"url": "https://example.com/someurl", "timeout": "test"},
    ])
    def test_invalid_config(self, config, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test create with invalid config"""
        step = get_goto_step(config)
        with pytest.raises(jmon.errors.StepValidationError):
            step.validate_steps()

    @pytest.mark.parametrize('config, expected_clients', [
        ('https://some-url', [jmon.client_type.ClientType.BROWSER_FIREFOX, jmon.client_type.ClientType.BROWSER_CHROME, jmon.client_type.ClientType.REQUESTS]),
        ({"url": "https://some-url"}, [jmon.client_type.ClientType.REQUESTS]),
    ])
    def test_supported_clients(self, config, expected_clients, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test supported clients is correctly set based on config"""
        step = get_goto_step(config)
        supported_clients = step.supported_clients

        assert supported_clients == expected_clients

    def test_selenium_success(self, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test execution selenium"""
        step = get_goto_step("https://some.example.com/url")

        mock_element_state = unittest.mock.MagicMock()

        class MockSeleniumInstance:
            get = unittest.mock.MagicMock()

        class MockState:
            selenium_instance = MockSeleniumInstance()
            element = mock_element_state

        mock_state = MockState()

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        # Ensure element has been reset to None
        assert mock_state.element is mock_state.selenium_instance
        mock_state.selenium_instance.get.assert_called_once_with('https://some.example.com/url')

    def test_execution_requests_failure_log(self, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test execution selenium error log after failure"""
        step = get_goto_step("https://example.com/url")

        mock_element_state = unittest.mock.MagicMock()

        class MockSeleniumInstance:
            get = unittest.mock.MagicMock(side_effect=selenium.common.exceptions.WebDriverException("Could not access URL"))

        class MockState:
            selenium_instance = MockSeleniumInstance()
            element = mock_element_state

        mock_state = MockState()

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == '\n'.join([
            'Root -> GoTo: Step failed',
            "Root -> GoTo: Message: Could not access URL\n"
        ])
        assert step._status is jmon.step_status.StepStatus.FAILED

    def test_requests_success(self, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test execution requests"""
        step = get_goto_step("https://some.example.com/url")

        class MockState:
            response = None

        mock_state = MockState()

        mock_request_response = unittest.mock.MagicMock()
        mock_requests_get = unittest.mock.MagicMock(return_value=mock_request_response)

        with unittest.mock.patch('requests.get', mock_requests_get):
            step.execute(execution_method="execute_requests", state=mock_state)

        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        # Ensure element has been reset to None
        assert mock_state.response is mock_request_response
        mock_requests_get.assert_called_once_with(url='https://some.example.com/url', headers={})

    def test_requests_full_config_body_success(self, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test execution requests with body"""
        step = get_goto_step({
            "url": "https://some.example.com/url",
            "body": "test body",
            "method": "post",
            "headers": {"test-header": "header-value"},
            "ignore-ssl": True,
            "timeout": 6,
        })

        class MockState:
            response = None

        mock_state = MockState()

        mock_request_response = unittest.mock.MagicMock()
        mock_requests_post = unittest.mock.MagicMock(return_value=mock_request_response)

        with unittest.mock.patch('requests.post', mock_requests_post):
            step.execute(execution_method="execute_requests", state=mock_state)

        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        # Ensure element has been reset to None
        assert mock_state.response is mock_request_response
        mock_requests_post.assert_called_once_with(
            url='https://some.example.com/url',
            headers={'test-header': 'header-value'},
            data='test body',
            verify=False,
            timeout=6,
        )

    def test_requests_full_config_json_success(self, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test execution requests with JSON"""
        step = get_goto_step({
            "url": "https://some.example.com/url",
            "json": {"some": ["post", "data"]},
            "method": "put",
            "headers": {"test-header": "header-value"},
            "ignore-ssl": True,
            "timeout": 7,
        })

        class MockState:
            response = None

        mock_state = MockState()

        mock_request_response = unittest.mock.MagicMock()
        mock_requests_put = unittest.mock.MagicMock(return_value=mock_request_response)

        with unittest.mock.patch('requests.put', mock_requests_put):
            step.execute(execution_method="execute_requests", state=mock_state)

        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        # Ensure element has been reset to None
        assert mock_state.response is mock_request_response
        mock_requests_put.assert_called_once_with(
            url='https://some.example.com/url',
            headers={'test-header': 'header-value'},
            json={"some": ["post", "data"]},
            verify=False,
            timeout=7,
        )

    def test_execution_requests_failure_log(self, mock_run, mock_root_step, mock_logger, get_goto_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test execution requests error log after failure"""
        step = get_goto_step("https://example.com/url")

        class MockState:
            response = None

        mock_state = MockState()

        mock_request_response = unittest.mock.MagicMock()
        mock_requests_get = unittest.mock.MagicMock(side_effect=requests.exceptions.ConnectionError("Could not access URL"))

        with unittest.mock.patch('requests.get', mock_requests_get):
            step.execute(execution_method="execute_requests", state=mock_state)

        assert mock_logger.read_log_stream() == '\n'.join([
            'Root -> GoTo: Step failed',
            "Root -> GoTo: Could not access URL\n"
        ])
        assert step._status is jmon.step_status.StepStatus.FAILED
