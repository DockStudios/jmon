
class JmonError(Exception):
    """Base JMON error"""

    pass


class CheckCreateError(JmonError):
    """Failed to create check"""

    pass


class EnvironmentCreateError(JmonError):
    """Failed to create environment"""

    pass


class EnvironmentHasRegisteredChecksError(JmonError):
    """An environment has checks registered against it"""

    pass


class StepValidationError(JmonError):
    """A validation error occurred with step"""

    pass


class UnableToPushMetricVictoriaMetricsError(JmonError):
    """Unable to push metric to victoriametrics"""

    pass
