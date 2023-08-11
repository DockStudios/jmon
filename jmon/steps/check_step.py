
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import RequestsStepState, SeleniumStepState
from jmon.steps.base_step import BaseStep
import jmon.steps.checks
from jmon.logger import logger


class CheckStep(BaseStep):
    """
    Directive for performing a check task.

    Each check directive may one or more checks.

    This can be placed in the root of the check, e.g.
    ```
     - goto: https://example.com
     - check:
         title: Example Page
         url: https://example.com/?followed=redirect
    ```

    It can also be placed within a find directive, e.g.:
    ```
     - goto: https://example.com
     - find:
       - tag: input
       - check:
           text: Enter input
    ```
    """

    CONFIG_KEY = "check"
    CHILD_STEPS_FORM_STEP = True

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME,
            ClientType.REQUESTS
        ]

    @property
    def supported_child_steps(self):
        """Return list of child support step classes"""
        return jmon.steps.checks.BaseCheck.__subclasses__()

    @property
    def id(self):
        """ID string for step"""
        return f"Checks"

    @property
    def description(self):
        """Friendly description of step"""
        return "Running check steps"

    def _validate_step(self):
        """Check step is valid"""
        if len(self.get_child_steps()) == 0:
            raise StepValidationError("At least one attribute must be provided for a check step")

    def get_child_steps(self):
        """
        Get child steps

        Support checks such as:
        - check:
            title: An example website
            response_code: 200
            url: https://www.example.com
        """
        if self._child_steps is None:
            self._child_steps = []

            supported_actions = self.get_supported_child_steps()

            for action_name in self._config:
                if action_name in supported_actions:
                    self._child_steps.append(
                        supported_actions[action_name](
                            run=self._run,
                            config=self._config[action_name],
                            parent=self
                        )
                    )
        return self._child_steps

    def execute_requests(self, state: RequestsStepState):
        """Execute step"""
        # Do nothing, let sub-checks perform checks
        pass

    def execute_selenium(self, state: SeleniumStepState):
        """Execute step"""
        # Do nothing, let sub-checks perform checks
        pass
