
import os

from flask import request

from jmon.database import Database
from jmon.errors import CheckCreateError

from . import FlaskApp
from .utils import get_check_and_environment_by_name
from jmon.models import Check


@FlaskApp.app.route('/api/v1/version', methods=["GET"])
def get_version():
    """Get jmon version"""
    version_file = os.path.join(os.curdir, 'VERSION')
    if os.path.isfile(version_file):
        with open(version_file, "r") as fh:
            return {"version": fh.read().strip()}
    return {"version": "unknown"}
