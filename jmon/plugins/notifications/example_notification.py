

from jmon.plugins import NotificationPlugin
from jmon.logger import logger


class ExampleNotification(NotificationPlugin):
    """Example notification plugin"""

    def on_first_success(self, check_name, run_status, run_log, attributes, **future_kwargs):
        """Handle first success"""
        # Custom attributes passed in from check configuration can be accessed via attributes
        customer_name = attributes.get('CUSTOMER_NAME', 'No customer name in check')
        logger.debug(f"{check_name} had has changed to success state: {customer_name}")

    def on_first_failure(self, check_name, run_status, run_log, attributes, **future_kwargs):
        """Handle first failure"""
        logger.debug(f"{check_name} had has changed to failure state")

    def on_every_success(self, check_name, run_status, run_log, attributes, **future_kwargs):
        """Handle every success"""
        logger.debug(f"{check_name} is passing")

    def on_every_failure(self, check_name, run_status, run_log, attributes, **future_kwargs):
        """Handle every failure"""
        logger.debug(f"{check_name} is failing")

    def on_every_timeout(self, check_name, run_status, run_log, attributes, **future_kwargs):
        """Handle every timeout"""
        logger.debug(f"{check_name} exceeded the check timeout")

    def on_complete(self, check_name, run_status, run_log, attributes, **future_kwargs):
        """Handle every run completion"""
        logger.debug(f"{check_name} has run with status: {run_status}")
        logger.debug(f"Log: {run_log}")

    def on_check_queue_timeout(self, check_count, **future_kwargs):
        """Handle queue timeout"""
        logger.warn(f"{check_count} check(s) missed due to queue timeout")
