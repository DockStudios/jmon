
import datetime
from typing import Any, Callable
import unittest.mock

import pytest

import jmon.step_status
import jmon.steps
import jmon.steps.checks
import jmon.errors
import jmon.client_type
import jmon.run_logger


class MockLogger(jmon.run_logger.RunLogger):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mock_log_lines = []

    def debug(self, msg):
        self._mock_log_lines.append(('debug', msg))

    def info(self, msg):
        self._mock_log_lines.append(('info', msg))

    def warn(self, msg):
        self._mock_log_lines.append(('warn', msg))

    def error(self, msg):
        self._mock_log_lines.append(('error', msg))

@pytest.fixture
def mock_run():
    run = unittest.mock.MagicMock()
    run.get_remaining_time.return_value = datetime.timedelta(minutes=1)
    yield run

@pytest.fixture
def mock_logger():
    logger = MockLogger(run=None, enable_log=True)
    yield logger
    logger.cleanup()

@pytest.fixture
def mock_root_step(mock_logger):
    yield jmon.steps.RootStep(run=None, config=None, parent=None, run_logger=mock_logger)

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

    def test_execution_requests_equals_match(self, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution requests using equals with valid match"""
        step = get_json_step({"equals": {"some_dict": "value", "another": {"nested": "value"}}})
        mock_state = unittest.mock.MagicMock()
        mock_state.response.json.return_value = {"some_dict": "value", "another": {"nested": "value"}}

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger._mock_log_lines == []
        assert step._status is jmon.step_status.StepStatus.SUCCESS

    def test_execution_requests_equals_mismatch(self, mock_run, mock_root_step, mock_logger, get_json_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution requests"""
        step = get_json_step({"equals": {"some_dict": "value"}})
        mock_state = unittest.mock.MagicMock()
        mock_state.response.json.return_value = {"doesnotexist": "value"}

        step.execute(execution_method="execute_requests", state=mock_state)
        assert mock_logger._mock_log_lines == []
        assert step._status is jmon.step_status.StepStatus.FAILED
