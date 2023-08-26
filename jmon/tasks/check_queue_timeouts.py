
from socket import timeout
import kombu
from celery.result import AsyncResult

from jmon import app, broker_url, dead_letter_queue
import jmon.config
from jmon.logger import logger
import jmon.database
import jmon.models
from jmon.plugins import NotificationLoader


def check_queue_timeouts():
    """
    Check for checks that timed out on queue
    """

    revoked_tasks = app.control.inspect().revoked()
    expired_tasks = 0
    for worker_id in revoked_tasks:
        for task_id in revoked_tasks[worker_id]:
            result = AsyncResult(task_id, app=app)

            # Check was revoked due to expiration
            # @TODO Check if task is of type perform_check
            # @TODO Obtain check name and environment for expired checks
            if str(result.result) == "expired":
                logger.info(f"Found missed check: {task_id}")
                expired_tasks += 1

                # Forget result, so it is not processed on next run
                result.forget()

    def process_deadletter_message(body, message):
        """Add dead letter message to expired tasks"""
        nonlocal expired_tasks
        logger.info(f"Found DLQ Check: {body[0]}")
        expired_tasks += 1
        message.ack()

    # Connect to deadletter queue and obtain any messages
    with kombu.Connection(broker_url) as conn:

        # Consum messages from the dead letter queue
        with conn.Consumer(dead_letter_queue, callbacks=[process_deadletter_message]) as consumer:
            # Perform one iteration of draining the queue with short
            # timeout to avoid waiting for a message to arrive to queue
            try:
                conn.drain_events(timeout=0.1)
            except timeout:
                logger.debug("No messages to drain from DLQ")

    if expired_tasks:
        # If an expired result was found, notify via
        # notification plugins
        for notification_plugin in NotificationLoader.get_instance().get_plugins():
            logger.debug(f"Processing notification plugin: {notification_plugin}")
            try:
                logger.debug(f"Calling notification plugin method: {notification_plugin}.on_check_queue_timeout")
                getattr(notification_plugin(), "on_check_queue_timeout")(check_count=expired_tasks)
            except Exception as exc:
                logger.warn(f"Failed to call notification method: {str(exc)}")

    # Clear down session
    jmon.database.Database.clear_session()
