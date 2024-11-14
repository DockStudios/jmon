
from typing import Any, Callable
import unittest.mock

import pytest
import requests.exceptions

import jmon.step_status
import jmon.steps
import jmon.steps.checks
import jmon.errors
import jmon.client_type
import jmon.run_logger
from test.unit.jmon.steps.fixtures import mock_run, mock_logger, mock_root_step


@pytest.fixture
def get_body_step(mock_run, mock_root_step, mock_logger) -> Callable[[Any], 'jmon.steps.checks.BodyCheck']:
    def inner(config):
        return jmon.steps.checks.BodyCheck(parent=mock_root_step, config=config, run=mock_run, run_logger=mock_logger)
    return inner


class TestBodyCheck:

    def _create_step(self, config):
        mock_run = unittest.mock.MagicMock()
        root_step = jmon.steps.RootStep(None, None, None)
        mock_logger = unittest.mock.MagicMock()
        step = jmon.steps.checks.BodyCheck(parent=root_step, config=config, run=mock_run, run_logger=mock_logger)
        return mock_run, mock_logger, step

    @pytest.mark.parametrize('config', [
        {"equals": "some_value"},
        {"contains": "some_value"},
        {"equals": "some_value"},
        {"contains": "some_value"},
    ])
    def test_create(self, config, mock_run, mock_root_step, mock_logger, get_body_step: Callable[[Any], 'jmon.steps.checks.BodyCheck']):
        """Test create with valid config"""
        step = get_body_step(config)
        step.validate_steps()

    @pytest.mark.parametrize('config', [
        None,
        # String value
        'string',
        # List value,
        ['Test Value'],

        # Dict without valid comparator
        {'something_else': 'value'}
    ])
    def test_invalid_config(self, config, mock_run, mock_root_step, mock_logger, get_body_step: Callable[[Any], 'jmon.steps.checks.BodyCheck']):
        """Test create with invalid config"""
        step = get_body_step(config)
        with pytest.raises(jmon.errors.StepValidationError):
            step.validate_steps()

    def test_supported_clients(self, mock_run, mock_root_step, mock_logger, get_body_step: Callable[[Any], 'jmon.steps.checks.BodyCheck']):
        """Test supported clients and ensure each method is implemented"""
        step = get_body_step({"equals": True})
        supported_steps = step.supported_clients

        mock_state = unittest.mock.MagicMock()

        if (jmon.client_type.ClientType.BROWSER_CHROME in supported_steps or
                jmon.client_type.ClientType.BROWSER_FIREFOX in supported_steps):
           step.execute_selenium(state=mock_state)
        else:
            with pytest.raises(NotImplementedError):
                step.execute_selenium(state=mock_state)
        if jmon.client_type.ClientType.REQUESTS in supported_steps:
           step.execute_requests(state=mock_state)
        else:
            with pytest.raises(NotImplementedError):
                step.execute_requests(state=mock_state)

    @pytest.mark.parametrize('config, body_response', [
        ({"equals": "This is a body"}, "This a different response"),
        ({"contains": "DoesItContainThis"}, "This a different response")
    ])
    def test_execution_requests_mismatch(self, config, body_response, mock_run, mock_root_step, mock_logger, get_body_step: Callable[[Any], 'jmon.steps.checks.BodyCheck']):
        """Test execution requests"""
        step = get_body_step(config)
        mock_state = unittest.mock.MagicMock()
        mock_state.response.content = body_response

        step.execute(execution_method="execute_requests", state=mock_state)
        assert 'Root -> CheckBody: Step failed' in mock_logger.read_log_stream()
        assert 'Root -> CheckBody: body match failed' in mock_logger.read_log_stream()
        assert step._status is jmon.step_status.StepStatus.FAILED

    @pytest.mark.parametrize('config, body_response', [
        ({"equals": "string match"}, "string match"),
        ({"contains": "part"}, "containspartstring"),
    ])
    def test_execution_requests_match(self, config, body_response, mock_run, mock_root_step, mock_logger, get_body_step: Callable[[Any], 'jmon.steps.checks.BodyCheck']):
        """Test execution requests with valid match"""
        step = get_body_step(config)
        mock_state = unittest.mock.MagicMock()
        mock_state.response.content = body_response

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS
 
    def test_execution_requests_mismatch_error_log(self, mock_run, mock_root_step, mock_logger, get_body_step: Callable[[Any], 'jmon.steps.checks.BodyCheck']):
        """Test execution requests error log after failure"""
        step = get_body_step({"contains": "does_not_exist"})
        mock_state = unittest.mock.MagicMock()
        mock_state.response.content = "Different response"

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger.read_log_stream() == '\n'.join([
            'Root -> CheckBody: Step failed',
            "Root -> CheckBody: body match failed: Could not find 'does_not_exist' in body",
            "Full body: Different response\n"
        ])
        assert step._status is jmon.step_status.StepStatus.FAILED

    def test_execution_requests_no_state(self, mock_run, mock_root_step, mock_logger, get_body_step: Callable[[Any], 'jmon.steps.checks.BodyCheck']):
        """Test execution requests without response state"""
        step = get_body_step({"equals": "value"})
        mock_state = unittest.mock.MagicMock()
        mock_state.response = None

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger.read_log_stream() == '\n'.join([
            'Root -> CheckBody: Step failed',
            'Root -> CheckBody: This step requires a request to have been made\n',
        ])
        assert step._status is jmon.step_status.StepStatus.FAILED
