
from jmon.run_logger import RunLogger


class StepLogger(RunLogger):
    """Logger interface for steps"""

    def __init__(self, step, should_info_debug_log):
        """Get step for log prefix"""
        self.log_prefix = f"{step.full_id}: "
        self.should_info_debug_log = should_info_debug_log
