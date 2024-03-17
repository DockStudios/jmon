
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
def get_json_step(mock_run, mock_root_step, mock_logger) -> Callable[[Any], 'jmon.steps.checks.JsonCheck']:
    def inner(config):
        return jmon.steps.checks.JsonCheck(parent=mock_root_step, config=config, run=mock_run, run_logger=mock_logger)
    return inner


class TestJsonCheck:

    def _create_step(self, config):
        mock_run = unittest.mock.MagicMock()
        root_step = jmon.steps.RootStep(None, None, None)
        mock_logger = unittest.mock.MagicMock()
        step = jmon.steps.checks.JsonCheck(parent=root_step, config=config, run=mock_run, run_logger=mock_logger)
        return mock_run, mock_logger, step

    @pytest.mark.parametrize('config', [
        {"equals": "some_value"},
        {"contains": "some_value"},
        {"equals": "some_value", "selector": ".test"},
        {"contains": "some_value", "selector": ".test"},
    ])
    def test_create(self, config, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test create with valid config"""
        step = get_json_step(config)
        step.validate_steps()

    @pytest.mark.parametrize('config', [
        # String value
        'string',
        # List value,
        ['Test Value'],

        # Dict without valid comparator
        {'something_else': 'value'}
    ])
    def test_invalid_config(self, config, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test create with invalid config"""
        step = get_json_step(config)
        with pytest.raises(jmon.errors.StepValidationError):
            step.validate_steps()

    def test_supported_clients(self, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test supported clients and ensure each method is implemented"""
        step = get_json_step({"equals": True})
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

    @pytest.mark.parametrize('config, json_response', [
        ({"equals": {"some_dict": "value"}}, {"doesnotexist": "value"})
    ])
    def test_execution_requests_mismatch(self, config, json_response, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution requests"""
        step = get_json_step(config)
        mock_state = unittest.mock.MagicMock()
        mock_state.response.json.return_value = json_response

        step.execute(execution_method="execute_requests", state=mock_state)
        assert 'Root -> CheckJson: Step failed' in mock_logger.read_log_stream()
        assert 'Root -> CheckJson: JSON match failed' in mock_logger.read_log_stream()
        assert step._status is jmon.step_status.StepStatus.FAILED

    @pytest.mark.parametrize('config, json_response', [
        ({"equals": "string match"}, "string match"),
        ({"equals": ["list", "match"]}, ["list", "match"]),
        ({"equals": {"some_dict": "value", "another": {"nested": "value"}}}, {"some_dict": "value", "another": {"nested": "value"}}),

        ({"contains": "part"}, "containspartstring"),

        ({"contains": "value"}, ["list", "value", "contains"]),
        ({"contains": "dictkey"}, {"dictkey": "exists", "another": "value"}),

        # With selector
        ({"equals": "string match", "selector": "$.nested[0]"}, {"nested": ["string match"]}),
        ({"equals": ["list", "match"], "selector": "$.nestedlist"}, {"nestedlist": ["list", "match"]}),
        ({"equals": "value", "selector": "$.another.nested"}, {"some_dict": "value", "another": {"nested": "value"}}),

        ({"contains": "part", "selector": "$.nested"}, {"nested": "containspartstring"}),

        ({"contains": "value", "selector": "$.nested"}, {"nested": ["list", "value", "contains"]}),
        ({"contains": "dictkey", "selector": "$.nested"}, {"nested": {"dictkey": "exists", "another": "value"}}),
    ])
    def test_execution_requests_match(self, config, json_response, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution requests with valid match"""
        step = get_json_step(config)
        mock_state = unittest.mock.MagicMock()
        mock_state.response.json.return_value = json_response

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS
 
    def test_execution_requests_mismatch_error_log(self, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution requests error log after failure"""
        step = get_json_step({"contains": "does_not_exist"})
        mock_state = unittest.mock.MagicMock()
        mock_state.response.json.return_value = ["first", "some_value", "other"]

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger.read_log_stream() == '\n'.join([
            'Root -> CheckJson: Step failed',
            "Root -> CheckJson: JSON match failed: Could not find 'does_not_exist' in actual value '['first', 'some_value', 'other']'",
            "Full Response: ['first', 'some_value', 'other']\n"
        ])
        assert step._status is jmon.step_status.StepStatus.FAILED

    def test_execution_requests_mismatch_error_log_with_selector(self, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution requests error log after failure with selector"""
        step = get_json_step({"contains": "does_not_exist", "selector": "$.doesnotexist"})
        mock_state = unittest.mock.MagicMock()
        mock_state.response.json.return_value = ["first", "some_value", "other"]

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger.read_log_stream() == '\n'.join([
            'Root -> CheckJson: Step failed',
            "Root -> CheckJson: JSON match failed: Could not find 'does_not_exist' in actual value '[]', from JSON selector '$.doesnotexist'",
            "Full Response: ['first', 'some_value', 'other']\n"
        ])
        assert step._status is jmon.step_status.StepStatus.FAILED

    def test_execution_requests_no_state(self, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution requests without response state"""
        step = get_json_step({"equals": "value"})
        mock_state = unittest.mock.MagicMock()
        mock_state.response = None

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger.read_log_stream() == '\n'.join([
            'Root -> CheckJson: Step failed',
            'Root -> CheckJson: This step requires a request to have been made\n',
        ])
        assert step._status is jmon.step_status.StepStatus.FAILED
