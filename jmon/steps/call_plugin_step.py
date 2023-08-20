
import requests
import selenium.common.exceptions
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.plugins import CallbackPluginLoader
from jmon.step_state import RequestsStepState, SeleniumStepState

from jmon.step_status import StepStatus
from jmon.steps.base_step import BaseStep
from jmon.logger import logger
from jmon.stubs.callable_plugin_stub_check import CallablePluginStubCheck
from jmon.stubs.callable_plugin_stub_run import CallablePluginStubRun
from jmon.stubs.callable_plugin_stub_step import CallablePluginStubStep
from jmon.stubs.plugin_sub_logger import PluginStubLogger


class CallPluginStep(BaseStep):
    """
    Directive for executing a callable plugin.

    This should generally always be used as a first directive of a step.

    It can be used multiple times during a check.

    This can be placed in the root of the check, e.g.
    ```
     - call_plugin:
         example-plugin:
           example_argument: 'example_value'
    ```
    """

    CONFIG_KEY = "call_plugin"

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME,
            ClientType.REQUESTS
        ]

    def _validate_step(self):
        """Check step is valid"""
        if type(self._config) is not dict or not self._config:
            raise StepValidationError("call_plugin value must an object of plugins to call")

        callable_plugin_loader = CallbackPluginLoader.get_instance()
        valid_plugin_names = [
            plugin.get_plugin_name()
            for plugin in callable_plugin_loader.get_plugins()
        ]

        # Iterate through each plugin name to call
        for plugin_name in self._config:
            # Ensure plugin exists
            if plugin_name not in valid_plugin_names:
                raise StepValidationError(
                    f"Attempt to call non-existent callbable plugin: {plugin_name}. "
                    "Available plugins: {', '.join(valid_plugin_names)}"
                )

    @property
    def supported_child_steps(self):
        """Return list of child support step classes"""
        return []

    @property
    def id(self):
        """ID string for step"""
        return f"CallPlugin"

    @property
    def description(self):
        """Friendly description of step"""
        return f"Call plugins: {', '.join(self._config.keys())}"

    def _execute_plugins(self):
        """Execute plugins"""
        for plugin_name in self._config:
            # Obtain plugin by name
            plugin = CallbackPluginLoader.get_instance().get_plugin_by_name(plugin_name)
            if not plugin:
                raise Exception(f"Could not find callable plugin: {plugin_name}")

            # Create stub objects for passing to plugin
            stub_check = CallablePluginStubCheck(self._run.check)
            stub_step = CallablePluginStubStep(self)
            stub_logger = PluginStubLogger(self._logger)
            stub_run = CallablePluginStubRun(self._run)

            # Create instance of plugin
            plugin_instance = plugin(
                check=stub_check,
                step=stub_step,
                logger=stub_logger,
                run=stub_run
            )

            try:
                # Call plugin
                plugin_instance.handle_call(
                    # Pass kwargs from plugin config, default to empty
                    # dict if None is passed
                    **(self._config[plugin_name] or {})
                )
            except Exception as exc:
                self._logger.error(f"Plugin ({plugin_name}) call failed: {exc}")

    def execute_requests(self, state: RequestsStepState):
        """Execute plugins"""
        self._execute_plugins()

    def execute_selenium(self, state: SeleniumStepState):
        """Execute plugins"""
        self._execute_plugins()