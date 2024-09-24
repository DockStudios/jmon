
from typing import Any, Callable
import unittest.mock

import selenium.common.exceptions
import pytest

import jmon.step_status
import jmon.steps
import jmon.steps.actions
import jmon.errors
import jmon.client_type
import jmon.run_logger
from test.unit.jmon.steps.fixtures import mock_run, mock_logger, mock_root_step


@pytest.fixture
def get_wait_step(mock_run, mock_root_step, mock_logger) -> Callable[[Any], 'jmon.steps.actions.WaitAction']:
    def inner(config):
        return jmon.steps.actions.WaitAction(parent=mock_root_step, config=config, run=mock_run, run_logger=mock_logger)
    return inner


class TestJsonCheck:

    def _create_step(self, config):
        mock_run = unittest.mock.MagicMock()
        root_step = jmon.steps.RootStep(None, None, None)
        mock_logger = unittest.mock.MagicMock()
        step = jmon.steps.actions.WaitAction(parent=root_step, config=config, run=mock_run, run_logger=mock_logger)
        return mock_run, mock_logger, step

    @pytest.mark.parametrize('config', [
        "visible",
        "present",
        "clickable",
        {"type": "visible"},
        {"type": "present"},
        {"type": "clickable"},
        {"type": "clickable", "timeout": 51},
    ])
    def test_create(self, config, mock_run, mock_root_step, mock_logger, get_wait_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test create with valid config"""
        step = get_wait_step(config)
        step.validate_steps()

    @pytest.mark.parametrize('config', [
        # Invalid type
        None,
        5,
        5.5,
        ['this', 'list'],

        # String value
        'invalidtype',
        # Invalid types in dict
        {"no": "type"},
        {"type": None},
        {"type": 1234},
        {"type": "visible", "timeout": "abc"},
    ])
    def test_invalid_config(self, config, mock_run, mock_root_step, mock_logger, get_wait_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test create with invalid config"""
        step = get_wait_step(config)
        with pytest.raises(jmon.errors.StepValidationError):
            step.validate_steps()

    def test_supported_clients(self, mock_run, mock_root_step, mock_logger, get_wait_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test supported clients and ensure each method is implemented"""
        step = get_wait_step({"type": "clickable", "timeout": 1})
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

    @pytest.mark.parametrize('config, method, expected_timeout', [
        ({"type": "present"}, "presence_of_element_located", 60),
        ({"type": "present", "timeout": 51}, "presence_of_element_located", 51),
    ])
    def test_execution_selenium(self, config, method, expected_timeout, mock_run, mock_root_step, mock_logger, get_wait_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution selenium"""
        with unittest.mock.patch(f"selenium.webdriver.support.expected_conditions.{method}", unittest.mock.MagicMock()) as MockUntilMethod, \
                unittest.mock.patch("selenium.webdriver.support.wait.WebDriverWait", unittest.mock.MagicMock()) as MockDriverWait:
    
            until_response = object()
            MockUntilMethod.return_value = until_response

            step = get_wait_step(config)
            mock_selenium_instance = unittest.mock.MagicMock()
            mock_element = unittest.mock.MagicMock()
            mock_state = unittest.mock.MagicMock()
            mock_state.selenium_instance = mock_selenium_instance
            mock_state.element = mock_element

            mock_wait_instance = unittest.mock.MagicMock()
            mock_wait_instance.until = unittest.mock.MagicMock()
            MockDriverWait.return_value = mock_wait_instance

            step.execute(execution_method="execute_selenium", state=mock_state)

            MockUntilMethod.assert_called_once_with(mock_element)
            MockDriverWait.assert_called_once_with(mock_selenium_instance, expected_timeout)
            mock_wait_instance.until.assert_called_once_with(until_response)

            assert step._status is jmon.step_status.StepStatus.SUCCESS

    def test_execution_selenium_timeout(self, mock_run, mock_root_step, mock_logger, get_wait_step: Callable[[Any], 'jmon.steps.checks.JsonCheck']):
        """Test execution selenium with timeout"""
        with unittest.mock.patch(f"selenium.webdriver.support.expected_conditions.visibility_of", unittest.mock.MagicMock()) as MockUntilMethod, \
                unittest.mock.patch("selenium.webdriver.support.wait.WebDriverWait", unittest.mock.MagicMock()) as MockDriverWait:
    
            until_response = object()
            MockUntilMethod.return_value = until_response

            step = get_wait_step({"type": "visible"})
            mock_selenium_instance = unittest.mock.MagicMock()
            mock_element = unittest.mock.MagicMock()
            mock_state = unittest.mock.MagicMock()
            mock_state.selenium_instance = mock_selenium_instance
            mock_state.element = mock_element

            mock_wait_instance = unittest.mock.MagicMock()
            mock_until = unittest.mock.MagicMock(side_effect=selenium.common.exceptions.TimeoutException())
            mock_wait_instance.until = mock_until
            
            MockDriverWait.return_value = mock_wait_instance

            step.execute(execution_method="execute_selenium", state=mock_state)

            MockUntilMethod.assert_called_once_with(mock_element)
            MockDriverWait.assert_called_once_with(mock_selenium_instance, 60)
            mock_wait_instance.until.assert_called_once_with(until_response)


            assert 'Root -> Wait: Timeout ocurred before wait completed' in mock_logger.read_log_stream()
            assert step._status is jmon.step_status.StepStatus.FAILED
