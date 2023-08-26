
from flask import request
import yaml

from jmon.result_database import (
    ResultDatabase, ResultMetricAverageSuccessRate,
    ResultMetricLatestStatus
)
from jmon.result_timeframe import ResultTimeframeFactory

from . import FlaskApp
from .utils import get_check_and_environment_by_name


@FlaskApp.app.route('/api/v1/checks/<check_name>/environments/<environment_name>/results', methods=["GET"])
def get_check_results(check_name, environment_name):
    """Register check"""

    timeframe_name = request.args.get('timeframe')
    timeframe = None
    if timeframe_name:
        timeframe = ResultTimeframeFactory.get_by_name(timeframe_name)

        if not timeframe:
            return {"status": "error", "msg": "Invalid timeframe"}

    check, _, error = get_check_and_environment_by_name(
        check_name=check_name, environment_name=environment_name)
    if error:
        return error, 404

    result_database = ResultDatabase()
    average_success = None
    if timeframe:
        average_success = check.get_success_rate(timeframe.get_from_timestamp())
    else:
        average_success = ResultMetricAverageSuccessRate().read(
            result_database=result_database, check=check)

    return {
        "average_success": average_success,
        "latest_status": ResultMetricLatestStatus().read(
            result_database=result_database, check=check)
    }, 200
