
import datetime

from flask import request

from jmon.models.run import RunTriggerType

from . import FlaskApp
from .utils import get_check_and_environment_by_name
from jmon.models import Run


@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/runs', methods=["GET"])
def get_check_runs(check_name, environment_name):
    """Obtain list of runs for given check and environment"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    if from_date:
        # Strip zulu, if present
        if from_date.endswith('Z'):
            from_date = from_date[:-1]
        try:
            from_date = datetime.datetime.fromisoformat(from_date)
        except:
            return {"status": "error", "msg": "Invalid from_date parameter"}, 400
    if to_date:
        # Strip zulu, if present
        if to_date.endswith('Z'):
            to_date = to_date[:-1]
        try:
            to_date = datetime.datetime.fromisoformat(to_date)
        except:
            return {"status": "error", "msg": "Invalid to_date parameter"}, 400

    return {
        run.timestamp_id: run.status.value
        for run in Run.get_by_check(
            check=check,
            trigger_type=RunTriggerType.SCHEDULED,
            from_date=from_date,
            to_date=to_date
        )
    }, 200
