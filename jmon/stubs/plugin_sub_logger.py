

class PluginStubLogger:
    """Stub logger for providing interface for logging to plugins"""

    def __init__(self, parent_logger):
        """Store parent logger"""
        self.__logger = parent_logger

    def debug(self, msg):
        """Debug log"""
        self.__logger.debug(msg)

    def info(self, msg):
        """Debug log"""
        self.__logger.info(msg)

    def warn(self, msg):
        """Debug log"""
        self.__logger.warn(msg)

    def error(self, msg):
        """Debug log"""
        self.__logger.error(msg)
