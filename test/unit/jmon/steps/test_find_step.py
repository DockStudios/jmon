
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
def get_find_step(mock_run, mock_root_step, mock_logger) -> Callable[[Any], 'jmon.steps.FindStep']:
    def inner(config):
        return jmon.steps.FindStep(parent=mock_root_step, config=config, run=mock_run, run_logger=mock_logger)
    return inner


class TestFindStep:

    @pytest.mark.parametrize('config', [
        [{"id": "test"}],
        # With methods
        [{"class": "test"}],

        [{"text": "test"}],
        [{"placeholder": "test"}],
        [{"tag": "test"}],

        [{"tag": "div", "text": "test"}],
        [{"tag": "div", "placeholder": "test"}],
        [{"tag": "div", "placeholder": "test"}],
    ])
    def test_create(self, config, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test create with valid config"""
        step = get_find_step(config)
        step.validate_steps()

    @pytest.mark.parametrize('config', [
        {"a": "dict"},
        "A_String",

        ["string"],
        [["list"]],
    ])
    def test_invalid_config(self, config, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test create with valid config"""
        step = get_find_step(config)
        with pytest.raises(jmon.errors.StepValidationError):
            step.validate_steps()

    def test_supported_clients(self, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Return list of supported clients"""
        find_step = get_find_step([{'id': 'test'}])
        assert find_step.supported_clients == [jmon.client_type.ClientType.BROWSER_FIREFOX, jmon.client_type.ClientType.BROWSER_CHROME]

    def test_supported_clients(self, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Return list of supported clients"""
        find_step = get_find_step([{'id': 'test'}])
        assert find_step.supported_child_steps == [
            jmon.steps.FindStep,
            jmon.steps.ActionStep,
            jmon.steps.CheckStep,
        ]

    def test_execute_by_id(self, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test variable injection"""
        step = get_find_step([{"id": 'test-div-id'}])

        target_selenium_element = unittest.mock.MagicMock()

        class MockSeleniumElement:
            find_element = unittest.mock.MagicMock(return_value=target_selenium_element)

        original_element = MockSeleniumElement()

        class MockState:
            selenium_instance = None
            element = original_element

        mock_state = MockState()

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        assert mock_state.element is target_selenium_element
        original_element.find_element.assert_called_once_with('id', 'test-div-id')

    def test_execute_by_class(self, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test variable injection"""
        step = get_find_step([{"class": 'test-class-id'}])

        target_selenium_element = unittest.mock.MagicMock()

        class MockSeleniumElement:
            find_element = unittest.mock.MagicMock(return_value=target_selenium_element)

        original_element = MockSeleniumElement()

        class MockState:
            selenium_instance = None
            element = original_element

        mock_state = MockState()

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        assert mock_state.element is target_selenium_element
        original_element.find_element.assert_called_once_with('class name', 'test-class-id')

    def test_execute_by_tag(self, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test find by tag"""
        step = get_find_step([{"tag": 'test-tag-name'}])

        target_selenium_element = unittest.mock.MagicMock()

        class MockSeleniumElement:
            find_element = unittest.mock.MagicMock(return_value=target_selenium_element)

        original_element = MockSeleniumElement()

        class MockState:
            selenium_instance = None
            element = original_element

        mock_state = MockState()

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        assert mock_state.element is target_selenium_element
        original_element.find_element.assert_called_once_with('tag name', 'test-tag-name')

    @pytest.mark.parametrize('config, xpath', [
        ([{"placeholder": "test-unittest-placeholder"}], ".//*[@placeholder='test-unittest-placeholder']"),
        ([{"text": "test-unittest-text"}], ".//*[contains(text(), 'test-unittest-text')]"),
        ([{"placeholder": "test-unittest-placeholder", "tag": "unittest-tag"}], ".//unittest-tag[@placeholder='test-unittest-placeholder']"),
        ([{"text": "test-unittest-text", "tag": "unittest-tag"}], ".//unittest-tag[contains(text(), 'test-unittest-text')]"),
    ])
    def test_execute_by_xpath(self, config, xpath, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test find by xpath"""
        step = get_find_step(config)

        target_selenium_element = unittest.mock.MagicMock()

        class MockSeleniumElement:
            find_element = unittest.mock.MagicMock(return_value=target_selenium_element)

        original_element = MockSeleniumElement()

        class MockState:
            selenium_instance = None
            element = original_element

        mock_state = MockState()

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        assert mock_state.element is target_selenium_element
        original_element.find_element.assert_called_once_with('xpath', xpath)

    def test_find_without_result(self, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test find without a result"""
        step = get_find_step([{"id": "test-id"}])

        class MockSeleniumElement:
            find_element = unittest.mock.MagicMock(return_value=None)

        original_element = MockSeleniumElement()

        class MockState:
            selenium_instance = None
            element = original_element

        mock_state = MockState()

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == (
            'Retrying step (1/5)\nRetrying step (2/5)\nRetrying step (3/5)\n'
            'Retrying step (4/5)\nRetrying step (5/5)\nRoot -> Find: Step failed\n'
        )
        assert step._status is jmon.step_status.StepStatus.FAILED

        assert mock_state.element is None
        original_element.find_element.assert_has_calls(calls=[
            unittest.mock.call("id", "test-id"),
            unittest.mock.call("id", "test-id"),
            unittest.mock.call("id", "test-id"),
            unittest.mock.call("id", "test-id"),
            unittest.mock.call("id", "test-id"),
        ])

    @pytest.mark.parametrize('exception', [
        selenium.common.exceptions.NoSuchElementException,
        selenium.common.exceptions.ElementNotInteractableException
    ])
    def test_find_selenium_exception(self, exception, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test find without a result"""
        step = get_find_step([{"id": "test-id"}])

        class MockSeleniumElement:
            find_element = unittest.mock.MagicMock(side_effect=exception)

        original_element = MockSeleniumElement()

        class MockState:
            selenium_instance = None
            element = original_element

        mock_state = MockState()

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == (
            'Root -> Find: Could not find element\nRetrying step (1/5)\n'
            'Root -> Find: Could not find element\nRetrying step (2/5)\n'
            'Root -> Find: Could not find element\nRetrying step (3/5)\n'
            'Root -> Find: Could not find element\nRetrying step (4/5)\n'
            'Root -> Find: Could not find element\nRetrying step (5/5)\n'
            'Root -> Find: Step failed\n'
        )
        assert step._status is jmon.step_status.StepStatus.FAILED

        assert mock_state.element is None
        original_element.find_element.assert_has_calls(calls=[
            unittest.mock.call("id", "test-id"),
            unittest.mock.call("id", "test-id"),
            unittest.mock.call("id", "test-id"),
            unittest.mock.call("id", "test-id"),
            unittest.mock.call("id", "test-id"),
        ])

    @pytest.mark.parametrize('config, call_args', [
        ([{"id": 'pre-{test_variable}-post'}],
         ('id', 'pre-unittest-value-post')),
        ([{"tag": 'pre-{test_variable}-post'}],
         ('tag name', 'pre-unittest-value-post')),
        ([{"class": 'pre-{test_variable}-post'}],
         ('class name', 'pre-unittest-value-post')),
        ([{"placeholder": 'pre-{test_variable}-post'}],
         ('xpath', ".//*[@placeholder='pre-unittest-value-post']")),
        ([{"text": 'pre-{test_variable}-post'}],
         ('xpath', ".//*[contains(text(), 'pre-unittest-value-post')]")),
        ([{"tag": "tag-pre-{test_variable}-post", "placeholder": 'pre-{test_variable}-post'}],
         ('xpath', ".//tag-pre-unittest-value-post[@placeholder='pre-unittest-value-post']")),
        ([{"tag": "tag-pre-{test_variable}-post", "text": 'pre-{test_variable}-post'}],
         ('xpath', ".//tag-pre-unittest-value-post[contains(text(), 'pre-unittest-value-post')]")),
    ])
    def test_variable_injection(self, config, call_args, mock_run, mock_root_step, mock_logger, get_find_step: Callable[[Any], 'jmon.steps.GotoStep']):
        """Test variable injection"""
        step = get_find_step(config)

        target_selenium_element = unittest.mock.MagicMock()

        class MockSeleniumElement:
            find_element = unittest.mock.MagicMock(return_value=target_selenium_element)

        original_element = MockSeleniumElement()

        class MockState:
            selenium_instance = None
            element = original_element

        mock_state = MockState()

        mock_run.variables = {'test_variable': 'unittest-value'}

        step.execute(execution_method="execute_selenium", state=mock_state)
        assert mock_logger.read_log_stream() == ''
        assert step._status is jmon.step_status.StepStatus.SUCCESS

        # Ensure element has been reset to None
        assert mock_state.element is target_selenium_element
        original_element.find_element.assert_called_once_with(*call_args)
