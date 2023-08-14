
from flask import request

from jmon.models.run import RunTriggerType

from . import FlaskApp
from .utils import get_check_and_environment_by_name
from jmon.models import Run
import jmon.tasks.perform_check


@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/runs', methods=["GET"])
def get_check_runs(check_name, environment_name):
    """Obtain list of runs for given check and environment"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    return {
        run.timestamp_id: run.status.value
        for run in Run.get_by_check(check=check, trigger_type=RunTriggerType.SCHEDULED)
    }, 200

@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/runs', methods=["POST"])
def trigger_run(check_name, environment_name):
    """Trigger run for check/environment"""
    check, environment, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    task = jmon.tasks.perform_check.perform_check.apply_async(
        args=(check.name, environment.name),
        kwargs={"trigger_type": RunTriggerType.MANUAL.value},
        options=check.task_options
    )
    return {
        "id": task.id
    }