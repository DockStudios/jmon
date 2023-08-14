
from re import L
from flask import request
from celery.result import AsyncResult

from . import FlaskApp
from .utils import get_check_and_environment_by_name
import jmon.models
import jmon.run
from jmon import app


@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/runs/<timestamp>', methods=["GET"])
def get_run_details(check_name, environment_name, timestamp):
    """Obtain run details"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404


    db_run = jmon.models.Run.get(
        check=check,
        timestamp_id=timestamp
    )
    if not db_run:
        return {
            "error": "Run does not exist"
        }, 400

    run = jmon.run.Run(check=check, db_run=db_run)

    return {
        "status": db_run.status.value,
        "artifacts": run.get_stored_artifacts()
    }

@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/run-trigger/<trigger_id>', methods=["GET"])
def get_trigger_run_details(check_name, environment_name, trigger_id):
    """Register check"""
    check, environment, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    task = AsyncResult(trigger_id, task_name="jmon.tasks.perform_check.perform_check", app=app)

    res = {
        "state": task.state
    }
    # If task is successful, return output (ID and result)
    if task.state == "SUCCESS":
        data = task.get()

        # Ensure check/environment match
        if data.get("check") != check.name or data.get("environment") != environment.name:
            return {"status": "error", "msg": "Run trigger does not exist"}, 404

        res.update(task.get())

    return res
