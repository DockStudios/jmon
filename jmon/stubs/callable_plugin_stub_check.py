

class CallablePluginStubCheck:
    """Stub check class that is passed to callable plugins"""

    @property
    def name(self):
        """Return name of check"""
        return self.__check.name

    @property
    def attributes(self):
        """Return dict of check attributes"""
        return self.__check.attributes

    def __init__(self, check):
        """Store check"""
        self.__check = check
