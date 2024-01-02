import datetime

from flask import request

from jmon.database import Database
from jmon.errors import CheckCreateError
from jmon.heatmap_timeframe import HeatmapTimeframeFactory
from jmon.result_database import ResultDatabase, ResultMetricHeatmapSuccessRate

from . import FlaskApp
from .utils import get_check_and_environment_by_name, require_api_key
from jmon.models import Check


@FlaskApp.app.route('/api/v1/checks', methods=["GET"])
def get_checks():
    """Register check"""
    checks = Check.get_all()
    return sorted(
        [
            {
                "name": check.name,
                "environment": check.environment.name,
                "enable": check.enabled
            }
            for check in checks
        ], key=lambda x: x["name"]
    ), 200


@FlaskApp.app.route('/api/v1/checks', methods=["POST"])
@require_api_key
def register_check():
    """Register check"""
    try:
        task = Check.from_yaml(request.data)
    except CheckCreateError as exc:
        return {"status": "error", "msg": str(exc)}, 400

    return {"status": "ok", "msg": "Check created/updated"}, 200

@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>', methods=["GET"])
def get_check(check_name, environment_name=None):
    """Get check details"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    return {
        "name": check.name,
        "client": check.client.value if check.client else None,
        "interval": check.interval,
        "calculated_interval": check.get_interval(),
        "timeout": check.timeout,
        "calculated_timeout": check.get_timeout(),
        "steps": check.steps,
        "enable": check.enabled,
        "step_count": check.get_step_count(),
        "supported_clients": [client.value for client in check.get_supported_clients()],
        "attributes": check.attributes,
        "screenshot_on_error": check.screenshot_on_error
    }, 200

@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>', methods=["DELETE"])
@require_api_key
def delete_check(check_name, environment_name):
    """Register check"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    check.delete()
    return {"status": "ok", "msg": "Check deleted"}, 200

@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/enable', methods=["POST"])
@require_api_key
def enable_check(check_name, environment_name):
    """Get check details"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    check.enable()

    return {
        "status": "ok", "msg": "Enabled check"
    }, 200

@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/disable', methods=["POST"])
@require_api_key
def disable_check(check_name, environment_name):
    """Get check details"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    check.disable()

    return {
        "status": "ok", "msg": "Disabled check"
    }, 200


@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/heatmap-data', methods=["GET"])
def get_check_heatmap_data(check_name, environment_name):
    """Get heatmap data"""
    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    if not from_date or not to_date:
        return {"status": "error", "msg": "from_date and to_date must be specified"}

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

    timeframe = HeatmapTimeframeFactory.get_by_time_difference(from_date=from_date, to_date=to_date)
    result_database = ResultDatabase()
    heatmap_metric = ResultMetricHeatmapSuccessRate()

    return [
        {
            "x": timeframe.get_label(data_point),
            "y": heatmap_metric.read(
                result_database=result_database,
                check=check,
                timeframe=timeframe,
                timestamp=data_point
            )
        }
        for data_point in timeframe.get_data_points(from_date=from_date, to_date=to_date)
    ]
