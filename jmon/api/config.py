
from . import FlaskApp
import jmon.config


@FlaskApp.app.route('/api/v1/config', methods=["GET"])
def get_config():
    """Register check"""
    config = jmon.config.Config.get()
    return {
        "check": {
            "thresholds": {
                "critical": config.CHECK_CRITICAL_THRESHOLD,
                "warning": config.CHECK_WARNING_THRESHOLD
            }
        }
    }, 200
