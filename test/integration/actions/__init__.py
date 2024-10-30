

import jmon.step_status
import jmon.steps
import jmon.steps.actions
import jmon.errors
import jmon.client_type
import jmon.run_logger
from test.unit.jmon.steps.fixtures import mock_run, mock_logger, mock_root_step


class TestWaitCheck:

    def test_execution_selenium(self):
        """Test execution selenium"""

        task = jmon.models.Check.from_yaml(
            """
name: IntegrationTestWait

steps:
  - goto: http://localhost:5000
"""
        )