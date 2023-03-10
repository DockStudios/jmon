
import functools
from flask import request

import jmon.models
import jmon.config


def get_check_and_environment_by_name(check_name, environment_name):
    """Return check and environment based on name"""
    environment = None
    if environment_name is not None:
        environment = jmon.models.environment.Environment.get_by_name(environment_name)
        if environment is None:
            return None, None, {"status": "error", "msg": "Environment does not exist"}

    check = jmon.models.check.Check.get_by_name_and_environment(check_name, environment)
    if not check:
        return None, None, {"status": "error", "msg": "Check does not exist"}

    return check, environment, None

def require_api_key(func):
    """Wrapper to check API key access"""
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        api_key = request.headers.get("X-JMon-Api-Key")
        required_api_key = jmon.config.Config.get().API_KEY

        # If an API key is defined in config and is either not provided or
        # does not match the required API key, return error
        if required_api_key and (not api_key or api_key != required_api_key):
            return {"message": "An API key is required"}, 403

        return func(*args, **kwargs)
    return decorator

