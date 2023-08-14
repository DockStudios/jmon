
from celery.result import AsyncResult

from jmon.models.run import RunTriggerType

from . import FlaskApp
from .utils import get_check_and_environment_by_name
import jmon.run
from jmon import app
import jmon.tasks.perform_check


@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/trigger', methods=["POST"])
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

@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/trigger/<trigger_id>', methods=["GET"])
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
