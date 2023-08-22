

class CallablePluginStubRun:
    """Stub Run class that is passed to callable plugins"""

    @property
    def variables(self):
        """Return runtime variables"""
        return self.__run.variables

    def __init__(self, run):
        """Store run"""
        self.__run = run

    def set_variable(self, key, value):
        """Set runtime variable"""
        self.__run.set_variable(key=key, value=value)
