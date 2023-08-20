"""Example callable plugin"""

from jmon.plugins import CallablePlugin


class ExampleCallablePlugin(CallablePlugin):
    """Example callable plugin"""

    """Define plugin name, for calling in check"""
    PLUGIN_NAME = "example-plugin"

    def handle_call(self, example_argument):
        """Handle call from check during run"""
        # Example logging
        self.logger.debug(f"Called callable plugin. Called with {example_argument}")

        # If passed example value is "fail", mark run as failed
        if example_argument == "fail":
            self.check.mark_step_as_failed()

        # Ensure check contains attribute "example_attribute"
        if "example_attribute" in self.check.attributes:
            # Use value of check attribute
            self.logger.info(f"Check has attribute \"example_attribute\": {self.check.attributes['example_attribute']}")

        # Logging can also be performed using:
        # self.logger.info("message")
        # self.logger.warn("message")
        # self.logger.error("message")
