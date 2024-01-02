
from typing import Dict, List
from datetime import datetime, timedelta

from jmon.config import Config


class HeatmapTimeframe:
    """Handle properties of result timeframes"""

    def __init__(self, name: str, format: str, expiry: timedelta, max_delta: timedelta, label_format: str):
        """Store member variables"""
        self._name = name
        self._format = format
        self._expiry = expiry
        self._max_delta = max_delta
        self._label_format = label_format

    @property
    def name(self) -> str:
        """Return name"""
        return self._name

    @property
    def format(self) -> str:
        """Return format"""
        return self._format

    @property
    def expiry(self) -> timedelta:
        """Return expiry"""
        return self._expiry

    def get_label(self, date: datetime):
        """Get label"""
        return date.strptime(self._label_format)

    def enabled_for_timeframe(self, from_date, to_date) -> bool:
        """Check if timeframe is available for from/to date"""
        return (to_date - from_date) <= self._max_delta

    def get_from_timestamp(self, date: datetime):
        """Return redis timestamp"""
        return date.strftime(self.format)

    def get_data_points(self, from_date: datetime, to_date: datetime) -> List[datetime]:
        """Return datetime points for timeframe within range"""
        return []



class HeatmapTimeframeFactory:
    """Factory class for returning heatmap timeframe instances"""

    _DEFINITIONS = {
        timeframe.name: timeframe
        for timeframe in [
            HeatmapTimeframe(
                name="hour",
                format="%Y%m%d%H",
                expiry=timedelta(minutes=Config().RESULT_RETENTION_MINS),
                max_delta=timedelta(hours=36),
                delta=timedelta(hours=1),
                label_format="%H:00"
            ),
            HeatmapTimeframe(
                name="day",
                format="%Y%m%d",
                expiry=timedelta(minutes=Config().RESULT_RETENTION_MINS),
                max_delta=timedelta(days=60),
                delta=timedelta(hours=24),
                label_format="%d %b"
            ),
            HeatmapTimeframe(
                name="month",
                format="%Y%m",
                expiry=timedelta(weeks=53),
                max_delta=timedelta(weeks=24),
                label_format="%b %Y",
                delta=relativetime,
            ),
        ]
    }

    @classmethod
    def get_by_time_difference(cls, from_date, to_date):
        """Get timeframe based on time difference"""
        for instance in cls.get_all():
            if instance.enabled_for_timeframe(from_date=from_date, to_date=to_date):
                return instance

    @classmethod
    def get_all(cls):
        """Return all result timeframes"""
        return [
            inst for inst in cls._DEFINITIONS.values()
        ]

    @classmethod
    def get_by_name(cls, name):
        """Return timeframe by name"""
        return cls._DEFINITIONS.get(name)
