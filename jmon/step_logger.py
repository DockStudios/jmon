
from jmon.run_logger import RunLogger


class StepLogger(RunLogger):
    """Logger interface for steps"""

    def __init__(self, step):
        """Get step for log prefix"""
        self.log_prefix = f"{step.full_id}: "
