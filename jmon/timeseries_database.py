
import abc
import datetime
from typing import Dict, List, Optional

import requests

import jmon.config
from jmon.heatmap_timeframe import HeatmapTimeframe, HeatmapTimeframeFactory
from jmon.result_timeframe import ResultTimeframe
import jmon.models.check
import jmon.models.run
import jmon.run



class TimeSeriesDatabase(abc.ABC):

    def __init__(self, url):
        """Store URL for timeseries database"""
        self._url = url

    @abc.abstractmethod
    def write_metric(self, metric_name: str, properties: Dict[str, str], fields: Dict[str, str], timestamp: datetime.datetime):
        """Write metric to database"""
        ...

    @abc.abstractmethod
    def read_metric(self, query: str, from_date: datetime.datetime, to_date: datetime.datetime):
        """Read metric from database"""
        ...


class VictoriaMetricsDatabase(TimeSeriesDatabase):
    """Implementation of TimeSeriesDatabase for victoriametrics"""

    def write_metric(self, metric_name: str, properties: Dict[str, str], fields: Dict[str, str], timestamp: datetime.datetime) -> bool:
        """Write metric to victoriametrics"""
        tags = [
            metric_name
        ]
        tags += [
            f"{key}={value}" for key, value in properties.items()
        ]
        fields_string = ','.join([
            f"{key}={value}" for key, value in fields.items()
        ])

        # Convert from seconds to microseconds and pad with 0s to nanoseconds
        timestamp_string = str(int(timestamp.timestamp() * 1000000)) + "000"

        data = f"{','.join(tags)} {fields_string} {timestamp_string}"
        res = requests.post(self._url + "/write", data=data)

        if res.status_code != 204:
            return False

        return True

    def read_metric(self, query: str, from_date: datetime.datetime, to_date: datetime.datetime) -> Optional[float]:
        """Read metric from database"""
        res = requests.get(self._url + "/prometheus/api/v1/query_range", params={
            "query": query,
            "start": from_date.isoformat() + 'Z',
            "end": to_date.isoformat() + 'Z',
            "step": str(int((to_date - from_date).total_seconds())) + "s"
        })

        # Try to obtain data from result
        results = res.json().get("data", {}).get("result", [])
        if results:
            if values := results[0].get("values", []):
                return float(values[0][1])
        return None


class TimeSeriesDatabaseFactory:

    @classmethod
    def get_database(cls):
        """Return instance of timeseries database based on available configs"""
        if vm_url := jmon.config.Config.get().VICTORIAMETRICS_URL:
            return VictoriaMetricsDatabase(url=vm_url)
        return None


class TimeSeriesMetric(abc.ABC):

    TIME_SERIES_METRIC_NAME = "jmon_result"


class TimeSeriesMetricWriter(TimeSeriesMetric):

    TIME_SERIES_METRIC_NAME = "jmon_result"

    @abc.abstractmethod
    def _get_write_properties(self, run: 'jmon.run.Run') -> Dict[str, str]:
        """Get properties to use when writing to time series database"""
        ...

    @abc.abstractmethod
    def _get_write_metrics(self, run: 'jmon.run.Run') -> Dict[str, float]:
        """Get value to write to time series database"""
        ...

    def write(self, result_database: 'TimeSeriesDatabase', run: 'jmon.run.Run'):
        """Write metric to result database"""
        result_database.write_metric(
            metric_name=self.TIME_SERIES_METRIC_NAME,
            properties=self._get_write_properties(run=run),
            fields=self._get_write_metrics(run=run),
            timestamp=run.run_model.timestamp
        )


class TimeSeriesMetricReader(TimeSeriesMetric):
    """Interface for reading metric"""

    @abc.abstractstaticmethod
    def _get_read_function():
        """Get function for querying metrics"""
        ...

    def _query_data(self, result_database: 'TimeSeriesDatabase',
                    check: 'jmon.models.check.Check',
                    filters: Dict[str, str],
                    from_date: datetime.datetime, to_date: datetime.datetime,
                    metric: str) -> float:
        """Query data from datasource"""
        filter_string = ", ".join([
            f'{key}="{value}"'
            for key, value in filters.items()
        ])
        lookback_seconds = (to_date - from_date).total_seconds()
        query_string = f'{self._get_read_function()}({self.TIME_SERIES_METRIC_NAME}_{metric}{{{filter_string}}}[{lookback_seconds}s])'
        # Since the metric is performing the lookback to start date,
        # as this appears to be more reliable than having a very large "step",
        # handling look backs over 1 month (or since start 1970).
        # The metric _must_ have a data point from the start-to
        from_date = (to_date - datetime.timedelta(seconds=check.get_interval() * 2))
        return result_database.read_metric(query=query_string, from_date=from_date, to_date=to_date)


class AverageCheckSuccessResultReader(TimeSeriesMetricReader):

    @staticmethod
    def _get_read_function():
        """Get function to query metrics"""
        return "avg_over_time"

    def get_data(self, result_database: 'TimeSeriesDatabase', check: 'jmon.models.check.Check',
                 from_date: Optional[datetime.datetime]=None, to_date: Optional[datetime.datetime]=None):
        """Return average success percentage"""
        if from_date is None:
            from_date = datetime.datetime.fromtimestamp(0)
        if to_date is None:
            to_date = datetime.datetime.now()

        return self._query_data(
            result_database=result_database,
            check=check,
            filters={"check": check.name, "environment": check.environment.name},
            to_date=to_date,
            from_date=from_date,
            metric="success"
        )


class RunResultMetricWriter(TimeSeriesMetricWriter):
    """Metric for run result"""

    def _get_write_properties(self, run: 'jmon.run.Run') -> Dict[str, str]:
        """Get properties to use when writing to time series database"""
        return {
            "check": run.check.name,
            "environment": run.check.environment.name,
        }

    def _get_write_metrics(self, run: 'jmon.run.Run') -> Dict[str, float]:
        """Get value to write to time series database"""
        return {
            "success": 1 if run.success else 0,
            "execution_time": run.execution_time
        }
