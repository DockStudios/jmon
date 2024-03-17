import unittest.mock
import datetime

import pytest

import test.unit.jmon.mock_run_logger
import jmon.steps

@pytest.fixture
def mock_run():
    run = unittest.mock.MagicMock()
    run.get_remaining_time.return_value = datetime.timedelta(minutes=1)
    yield run

@pytest.fixture
def mock_logger():
    logger = test.unit.jmon.mock_run_logger.MockLogger(run=None, enable_log=True)
    yield logger
    logger.cleanup()

@pytest.fixture
def mock_root_step(mock_logger):
    yield jmon.steps.RootStep(run=None, config=None, parent=None, run_logger=mock_logger)
