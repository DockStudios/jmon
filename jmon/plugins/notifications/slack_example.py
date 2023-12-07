
import os
import requests

from jmon.plugins import NotificationPlugin
from jmon.logger import logger


class SlackExample(NotificationPlugin):
    """
    Example functional slack notification plugin.

    To use this plugin, set JMon environment variables:
     * SLACK_WEBHOOK_URL (to send notification a single slack channel); or
     * SLACK_TOKEN (a slack app token, with permissions to post messages to public channels)
     * BASE_URL (optional) - base URL of JMon (e.g. https://jmon.example.com) to include URLs to failed checks in messages

    If using SLACK_TOKEN, each check must be defined with an attribute of 'notification_slack_channel'
    with the value of the name of the slack channel to send alerts to.
    """

    _WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
    _SLACK_TOKEN = os.environ.get("SLACK_TOKEN")

    def _post_webhook(self, text):
        """Send slack message via webhook URL"""
        res = requests.post(
            self._WEBHOOK_URL,
            json={
                "text": text
            }
        )
        if res.json().get("ok") is not True:
            logger.error("Slack did not return an OK status when posting notification")

    def _post_slack_app(self, text, slack_channel):
        """Send slack message via slack hook, obtaining slack channel from check attributes"""
        res = requests.post(
            "https://slack.com/api/chat.postMessage",
            json={
                "text": text,
                "channel": slack_channel
            },
            headers={
                "Authorization": f"Bearer {self._SLACK_TOKEN}"
            }
        )
        if res.json().get("ok") is not True:
            logger.error("Slack did not return an OK status when posting notification")

    def _post_message(self, text, attributes):
        """Send message to slack"""
        # If slack token is defined in environment variables
        # and check attributes contain a "notification_slack_channel",
        # send via app API
        if self._SLACK_TOKEN and (slack_channel := attributes.get("notification_slack_channel")):
            self._post_slack_app(text, slack_channel)

        # If a global slack webhook URL has been provided,
        # post using this
        elif self._WEBHOOK_URL:
            self._post_webhook(text)

        else:
            logger.debug("Slack not enabled")

    def _get_check_url(self, check_name, environment_name, run_timestamp):
        """Obtain URL using environment variable for base URL"""
        if base_url := os.environ.get("BASE_URL"):
            return f"{base_url}/checks/{check_name}/environments/{environment_name}/runs/{run_timestamp}"

    def on_first_failure(self, check_name, environment_name, run_timestamp, attributes, **kwargs):
        """Post slack message on failure"""
        message = f"{check_name} ({environment_name}) has failed :alarm:"
        if url := self._get_check_url(check_name=check_name, environment_name=environment_name, run_timestamp=run_timestamp):
            message += f"\n{url}"
        self._post_message(message, attributes)

    def on_first_timeout(self, check_name, environment_name, run_timestamp, attributes, **kwargs):
        """Post slack message on failure"""
        message = f"{check_name} ({environment_name}) has timed out :alarm:"
        if url := self._get_check_url(check_name=check_name, environment_name=environment_name, run_timestamp=run_timestamp):
            message += f"\n{url}"
        self._post_message(message, attributes)

    def on_first_success(self, check_name, environment_name, attributes, **kwargs):
        """Post slack message on success"""
        self._post_message(f"{check_name} ({environment_name}) is back to normal :white_check_mark:", attributes)

    def on_check_queue_timeout(self, check_count, **kwargs):
        """Handle queue timeout"""
        self._post_message(
            f"WARNING: {check_count} check(s) missed due to queue timeout. "
            "Check queue size and consider increase workers.",
            {}
        )
