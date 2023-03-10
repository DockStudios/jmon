
from flask import request
import yaml

from jmon.database import Database
from jmon.errors import CheckCreateError

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
