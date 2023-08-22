
from . import FlaskApp
import jmon.config
from jmon.result_timeframe import ResultTimeframeFactory


@FlaskApp.app.route('/api/v1/result-timeframes', methods=["GET"])
def get_timeframes():
    """Return list of timeframes"""
    return [
        {"name": timeframe.name, "friendly_name": timeframe.friendly_name}
        for timeframe in ResultTimeframeFactory.get_all()
    ], 200
