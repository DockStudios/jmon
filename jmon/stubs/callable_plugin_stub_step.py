
from jmon.step_status import StepStatus

class CallablePluginStubStep:
    """Stub step class that is passed to callable plugins"""

    def __init__(self, step):
        """Store step"""
        self.__step = step

    def mark_step_as_failed(self):
        """Mark step as failed"""
        self.__step.set_status(StepStatus.FAILED)
