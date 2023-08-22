
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


class CallablePlugin:
    """Base class for Callable plugins"""

    PLUGIN_NAME = None

    @property
    def check(self):
        """Return instance of check to obtain information about the check executing the plugin."""
        return self._check

    @property
    def step(self):
        """Return instance of step to access methods for interacting with the run."""
        return self._step

    @property
    def logger(self):
        """Return instance of logger for logging from plugin."""
        return self._logger

    @property
    def run(self):
        """Return instance of run for accessing properties and methods that related to the entire run"""
        return self._run

    def __init__(self, check, step, logger, run):
        """Store member variables for check and step"""
        self._check = check
        self._step = step
        self._logger = logger
        self._run = run

    @classmethod
    def get_plugin_name(cls):
        """Get plugin name"""
        if cls.PLUGIN_NAME is None:
            raise NotImplementedError
        return cls.PLUGIN_NAME

    def handle_call(self, **kwargs):
        """Handle call from check"""
        # Must be implemented by plugins
        raise NotImplementedError


class BasePluginLoader:

    _INSTANCE = None

    def __init__(self):
        """Setup loader"""
        self._plugins = None
        self._load_plugins()

    @classmethod
    def _load_plugins(cls):
        """Method to load plugins"""
        raise NotImplementedError

    @classmethod
    def get_instance(cls):
        """Get singleton instance of notification loader"""
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    def get_plugins(self):
        """Return all notification classes"""
        return self._load_plugins()


class CallbackPluginLoader(BasePluginLoader):
    """Factory for callbable plugins"""

    _PLUGIN_LOOKUP = None

    def get_plugin_by_name(self, plugin_name):
        """Obtain plugin by name"""
        if self._PLUGIN_LOOKUP is None:
            self._load_plugins()

        return self._PLUGIN_LOOKUP.get(plugin_name)

    def _load_plugins(self):
        """Try to load plugins"""
        if self._plugins is None:
            try:
                import jmon.plugins.callable
                for _module in jmon.plugins.callable.__all__:
                    __import__(f"jmon.plugins.callable.{_module}", globals(), {})
            except Exception as exc:
                logger.error(f"Failed to load plugins: {str(exc)}")
            self._plugins = [
                _class
                for _class in CallablePlugin.__subclasses__()
            ]

            self._PLUGIN_LOOKUP = {
                plugin.get_plugin_name(): plugin
                for plugin in self._plugins
            }

        return self._plugins


class NotificationLoader(BasePluginLoader):

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
