
import os
import requests

from jmon.plugins import NotificationPlugin
from jmon.logger import logger


class SlackExample(NotificationPlugin):

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

    def on_first_failure(self, check_name, attributes, **kwargs):
        """Post slack message on failure"""
        self._post_message(f"{check_name} has failed :alarm:", attributes)

    def on_first_timeout(self, check_name, attributes, **kwargs):
        """Post slack message on failure"""
        self._post_message(f"{check_name} has timed out :alarm:", attributes)

    def on_first_success(self, check_name, attributes, **kwargs):
        """Post slack message on success"""
        self._post_message(f"{check_name} is back to normal :white_check_mark:", attributes)

    def on_check_queue_timeout(self, check_count, **kwargs):
        """Handle queue timeout"""
        self._post_message(
            f"WARNING: {check_count} check(s) missed due to queue timeout. "
            "Check queue size and consider increase workers.",
            {}
        )
