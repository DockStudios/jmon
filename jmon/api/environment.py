
from flask import request

from jmon.errors import EnvironmentCreateError, JmonError

from . import FlaskApp
from .utils import require_api_key
import jmon.models


@FlaskApp.app.route('/api/v1/environments', methods=["POST"])
@require_api_key
def create_environment():
    """Create environment"""
    environment_name = request.json.get("name")
    if not environment_name:
        return {"status": "error", "msg": "Name not provided"}, 400

    try:
        jmon.models.environment.Environment.create(name=environment_name)
    except EnvironmentCreateError as exc:
        return {"status": "error", "msg": str(exc)}, 400

    return {"status": "ok", "msg": "Environment created"}, 200

@FlaskApp.app.route('/api/v1/environments/<environment_name>', methods=["DELETE"])
@require_api_key
def delete_environment(environment_name):
    """Delete environment"""
    environment = jmon.models.environment.Environment.get_by_name(name=environment_name)
    if not environment:
        return {"status": "error", "msg": "Environment does not exist"}, 404

    try:
        environment.delete()
    except JmonError as exc:
        return {"status": "error", "msg": str(exc)}
    return {"status": "ok", "msg": "Environment deleted"}, 200

@FlaskApp.app.route('/api/v1/environments/<environment_name>', methods=["GET"])
def get_environment(environment_name):
    """Create environment"""
    environment = jmon.models.environment.Environment.get_by_name(name=environment_name)
    if not environment:
        return {"status": "error", "msg": "Environment does not exist"}, 404

    return {
        "name": environment.name
    }, 200
