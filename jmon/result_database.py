
import datetime
import redis

import jmon.config
from jmon.heatmap_timeframe import HeatmapTimeframe, HeatmapTimeframeFactory
from jmon.result_timeframe import ResultTimeframe
import jmon.models.check
import jmon.run


class ResultMetric:

    def write(self, connection):
        """Base method to write result to redis"""
        raise NotImplementedError

    def read(self, connection):
        """Base method to read result from redis"""
        raise NotImplementedError


class AgentTaskClaim(ResultMetric):
    """Handle agent claiming task by ID to avoid duplicates"""

    def write(self, result_database, task_id):
        """Perform increment of task ID redis key to determine how many agents have picked up the task"""
        # Perform the increment
        key_ = f"task_agent_assignment:{task_id}"
        res = result_database.connection.incr(key_)

        # Set expiry on the key, set to 2x the max queue timeout
        # It could be the max queue timeout, but isn't much data and safer to
        # have a buffer
        result_database.connection.expire(
            f"task_agent_assignment:{task_id}",
            (jmon.config.Config.get().MAX_CHECK_QUEUE_TIME * 2)
        )

        # If result is 1, meaning this is the first
        # registration of the task, return True
        if res == 1:
            return True
        # Otherwise, return False as this task has already been picked up
        return False


class ResultMetricAverageSuccessRate(ResultMetric):
    """Metric for average success rate"""

    def _get_name(self):
        """Get name of metric"""
        return "jmon_result_metric_average_availability"

    def _get_key(self, check, success):
        """Get key from check"""
        success_key_part = "success" if success else "failure"
        return f"{check.name}_{check.environment.name}_{success_key_part}"

    def write(self, result_database, run):
        """Increment count for success/failure for run"""
        result_database.connection.hincrby(self._get_name(), self._get_key(run.check, run.success))

    def read(self, result_database, check):
        """Get success rate fraction"""
        # Get average successes/failures
        successes = int(result_database.connection.hget(self._get_name(), self._get_key(check, True)) or 0)
        failures = int(result_database.connection.hget(self._get_name(), self._get_key(check, False)) or 0)

        # Handle no checks
        if (successes + failures) == 0:
            return None
        return successes / (successes + failures)


class ResultMetricLatestStatus(ResultMetric):
    """Metric for latest result status"""

    def _get_name(self):
        """Get name of metric"""
        return "jmon_result_metric_latest_status"

    def _get_key(self, check):
        """Get key from check"""
        return f"{check.name}_{check.environment.name}"

    def write(self, result_database, run):
        """Write result to redis"""
        result_database.connection.hset(self._get_name(), self._get_key(run.check), 1 if run.success else 0)

    def read(self, result_database, check):
        """Get latest check result status"""
        # Get average successes/failures
        result = result_database.connection.hget(self._get_name(), self._get_key(check))
        if result is None:
            return None

        result = int(result.decode('utf-8'))

        # Return True/False based on 1 or 2
        if result == 1:
            return True
        elif result == 0:
            return False
        # Default to None (not run), assuming the metric doesn't exist
        return None


class ResultMetricHeatmapSuccessRate(ResultMetric):
    """Metric for success rate over time frame"""

    def _get_key(self, success: bool, check: 'jmon.models.check.Check', timeframe: HeatmapTimeframe, timestamp: datetime):
        """Get key from check"""
        suffix = "success" if success else "failure"
        return f"jmon_result_heatmap_{check.name}_{check.environment.name}_{timeframe.get_from_timestamp(timestamp)}_{suffix}"

    def write(self, result_database: 'ResultDatabase', run: 'jmon.run.Run'):
        """Write results to redis"""
        for timeframe in HeatmapTimeframeFactory.get_all():
            key_ = self._get_key(success=run.success, check=run.check, timeframe=timeframe, timestamp=run._db_run.timestamp)
            res = result_database.connection.incr(key_, amount=1)
            # If result is 1,
            # then the key has been created and expiry should be set
            if res == 1:
                result_database.connection.expire(
                    key_,
                    timeframe.expiry
                )

    def read(self, result_database: 'ResultDatabase', check: 'jmon.models.check.Check', timeframe: HeatmapTimeframe, timestamp: datetime):
        """Get latest check result status"""
        # Get passes/fails
        successes = result_database.connection.get(self._get_key(
            success=True, check=check, timeframe=timeframe, timestamp=timestamp
        ))
        if successes is None:
            successes = 0
        else:
            successes = int(successes)

        failures = result_database.connection.get(self._get_key(
            success=False, check=check, timeframe=timeframe, timestamp=timestamp
        ))
        if failures is None:
            failures = 0
        else:
            failures = int(failures)

        if (failures + successes) == 0:
            return None

        return (successes / (successes + failures)) * 100.0


class ResultDatabase:

    def __init__(self):
        """Create connection to redis"""
        config = jmon.config.Config.get()

        self._connection = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT, 
            password=config.REDIS_PASSWORD
        )

    @property
    def connection(self):
        """Return connection"""
        return self._connection
