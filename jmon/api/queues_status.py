
import os

from flask import request

from jmon.database import Database
from jmon.errors import CheckCreateError

from . import FlaskApp
from jmon import app


@FlaskApp.app.route('/api/v1/status/queues', methods=["GET"])
def queue_status():
    """Get Queue status info"""
    agent_count = {
        "default": 0,
        "firefox": 0,
        "chrome": 0,
        "requests": 0
    }
    # Process all queues for all agents and add to stats
    queues = app.control.inspect().active_queues()
    # Queues is None when there are no agents
    if queues:
        for agent in queues:
            for queue in queues[agent]:
                queue_name = queue.get("name")
                if queue_name and queue_name in agent_count:
                    agent_count[queue_name] += 1

    return {
        "queue_agent_count": agent_count
    }
