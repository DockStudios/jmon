"""Example callable plugin"""

from jmon.plugins import CallablePlugin


class ExampleCallablePlugin(CallablePlugin):
    """Example callable plugin"""

    """Define plugin name, for calling in check"""
    PLUGIN_NAME = "example-plugin"

    def handle_call(self, example_argument):
        """Handle call from check during run"""
        # Example logging
        # Logging can also be performed using:
        # self.logger.info("message")
        # self.logger.warn("message")
        # self.logger.error("message")
        self.logger.debug(f"Called callable plugin. Called with {example_argument}")

        # If passed example value is "fail", mark run as failed
        if example_argument == "fail":
            self.check.mark_step_as_failed()

        # Access check attributes, defined in the check definition.
        # These are read-only and modifying the attributes will have no effect
        if "example_attribute" in self.check.attributes:
            # Use value of check attribute
            self.logger.info(f"Check has attribute \"example_attribute\": {self.check.attributes['example_attribute']}")

        # Access and modify run variables, which can be used within other steps and plugins
        # self.
        # E.g. Check if a variable exists. If it does not exist, create one. Otherwise, log the value.
        if "variable_set_by_example_plugin" not in self.run.variables:
            self.logger.info(f"Set variable variable_set_by_example_plugin already set to new value: created_value")
            self.run.set_variable("variable_set_by_example_plugin", "created_value")
        else:
            self.logger.info(f"Variable variable_set_by_example_plugin already set to value: {self.run.variables['variable_set_by_example_plugin']}")
