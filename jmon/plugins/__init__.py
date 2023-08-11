
from jmon.logger import logger


class NotificationPlugin:

    def on_first_failure(self, check_name, run_status, run_log, attributes):
        """Handle result on first failure"""
        pass

    def on_every_failure(self, check_name, run_status, run_log, attributes):
        """Handle result on each failure"""
        pass

    def on_first_success(self, check_name, run_status, run_log, attributes):
        """Handle result on first success after a failure"""
        pass

    def on_every_success(self, check_name, run_status, run_log, attributes):
        """Handle result on success failure"""
        pass

    def on_complete(self, check_name, run_status, run_log, attributes):
        """Handle result on run completion"""
        pass

    def on_check_queue_timeout(self, check_count):
        """Handle checks missed due to queue timeout."""
        pass


class NotificationLoader:

    _INSTANCE = None

    def __init__(self):
        """Setup loader"""
        self._plugins = None
        self._load_plugins()

    def _load_plugins(self):
        """Try to load plugins"""
        if self._plugins is None:
            try:
                import jmon.plugins.notifications
                for _module in jmon.plugins.notifications.__all__:
                    __import__(f"jmon.plugins.notifications.{_module}", globals(), {})
            except Exception as exc:
                logger.error(f"Failed to load plugins: {str(exc)}")
            self._plugins = [
                _class
                for _class in NotificationPlugin.__subclasses__()
            ]
        return self._plugins

    @classmethod
    def get_instance(cls):
        """Get singleton instance of notification loader"""
        if cls._INSTANCE is None:
            cls._INSTANCE = NotificationLoader()
        return cls._INSTANCE

    def get_plugins(self):
        """Return all notification classes"""
        return self._load_plugins()
