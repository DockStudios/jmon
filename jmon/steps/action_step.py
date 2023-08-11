
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.steps.base_step import BaseStep
import jmon.steps.actions
from jmon.logger import logger

class ActionStep(BaseStep):
    """
    Directive for performing an action task.

    Each action directive may one or more actions.

    This can be placed in the root of the check, e.g.
    ```
     - goto: https://example.com
     - actions:
       - click
    ```

    It can also be placed within a find directive, e.g.:
    ```
     - goto: https://example.com
     - find:
       - tag: input
       - actions:
         - type: Pabalonium
         - press: enter
    ```
    """

    CONFIG_KEY = "actions"
    CHILD_STEPS_FORM_STEP = True

    @property
    def supported_child_steps(self):
        """Return list of child support step classes"""
        return jmon.steps.actions.BaseAction.__subclasses__()

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME
        ]

    def _validate_step(self):
        """Check step is valid"""
        if len(self.get_child_steps()) == 0:
            raise StepValidationError("At least one action must be provided")

    @property
    def id(self):
        """ID string for step"""
        return f"Actions"

    @property
    def description(self):
        """Friendly description of step"""
        return "Running action steps"

    def get_child_steps(self):
        """
        Get child steps

        Handle actions similar to:
        actions:
         - type: Pabalonium
         - press: enter
         - click
        """
        if self._child_steps is None:
            self._child_steps = []

            supported_actions = self.get_supported_child_steps()

            for action_config in self._config:
                if type(action_config) is dict:
                    for action_name in action_config:
                        if action_name in supported_actions:
                            self._child_steps.append(
                                supported_actions[action_name](
                                    run=self._run,
                                    config=action_config[action_name],
                                    parent=self
                                )
                            )
                elif type(action_config) is str:
                    self._child_steps.append(
                        supported_actions[action_config](run=self._run, config=None, parent=self)
                    )
        return self._child_steps

    def execute_selenium(self, state: SeleniumStepState):
        """Do nothihng"""
        # Do nothing, let sub-actions perform actions
        pass
