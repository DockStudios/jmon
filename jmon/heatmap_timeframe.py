
from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import datetime, timedelta

from jmon.config import Config


class HeatmapTimeframe(ABC):
    """Handle properties of result timeframes"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return name"""
        ...

    @property
    @abstractmethod
    def format(self) -> str:
        """Return format"""
        ...

    @property
    @abstractmethod
    def expiry(self) -> timedelta:
        """Return expiry"""
        ...

    @abstractmethod
    def get_label(self, date: datetime):
        """Get label"""
        return date.strftime(self.label_format)

    @property
    @abstractmethod
    def max_delta(self) -> timedelta:
        ...

    def enabled_for_timeframe(self, from_date: datetime, to_date: datetime) -> bool:
        """Check if timeframe is available for from/to date"""
        return abs(to_date - from_date) <= self.max_delta

    def get_from_timestamp(self, date: datetime):
        """Return redis timestamp"""
        return date.strftime(self.format)

    def get_data_points(self, from_date: datetime, to_date: datetime) -> List[datetime]:
        """Return datetime points for timeframe within range"""
        current_date = from_date
        points = []
        while current_date <= to_date:
            points.append(current_date)
            current_date = self.increment_date(current_date)
        return points

    @abstractmethod
    def increment_date(self, current_date: datetime) -> datetime:
        ...


class HeatmapTimeframeFiveMinute(HeatmapTimeframe):

    MINUTE_INTERVAL = 5

    @property
    def name(self) -> str:
        return "15-minute"

    def get_label(self, date: datetime):
        """Get label"""
        return date.strftime("%H:%M")

    @property
    def max_delta(self) -> timedelta:
        return timedelta(hours=2)

    @property
    def expiry(self) -> timedelta:
        return timedelta(minutes=Config().RESULT_RETENTION_MINS)

    @property
    def format(self) -> str:
        """Return format"""
        return "%Y%m%d%H%M"

    def get_from_timestamp(self, date: datetime):
        """Return redis timestamp"""
        # Round date down to nearest 15 minutes
        date = date - timedelta(minutes=date.minute % self.MINUTE_INTERVAL)
        return date.strftime(self.format)

    def increment_date(self, current_date: datetime) -> datetime:
        return current_date + timedelta(minutes=self.MINUTE_INTERVAL)


class HeatmapTimeframeHour(HeatmapTimeframe):

    @property
    def name(self) -> str:
        return "hour"

    def get_label(self, date: datetime):
        """Get label"""
        return date.strftime("%H:00")

    @property
    def max_delta(self) -> timedelta:
        return timedelta(hours=36)

    @property
    def expiry(self) -> timedelta:
        return timedelta(minutes=Config().RESULT_RETENTION_MINS)

    @property
    def format(self) -> str:
        """Return format"""
        return "%Y%m%d%H"

    def increment_date(self, current_date: datetime) -> datetime:
        return current_date + timedelta(hours=1)


class HeatmapTimeframeDay(HeatmapTimeframe):

    @property
    def name(self) -> str:
        return "day"

    def get_label(self, date: datetime):
        """Get label"""
        return date.strftime("%d %b")

    @property
    def max_delta(self) -> timedelta:
        return timedelta(days=60)

    @property
    def expiry(self) -> timedelta:
        return timedelta(minutes=Config().RESULT_RETENTION_MINS)

    @property
    def format(self) -> str:
        """Return format"""
        return "%Y%m%d"

    def increment_date(self, current_date: datetime) -> datetime:
        return current_date + timedelta(hours=24)


class HeatmapTimeframeMonth(HeatmapTimeframe):

    @property
    def name(self) -> str:
        return "month"

    def get_label(self, date: datetime):
        """Get label"""
        return date.strftime("%b %Y")

    @property
    def max_delta(self) -> timedelta:
        return timedelta(weeks=240)

    @property
    def expiry(self) -> timedelta:
        return timedelta(weeks=53)

    @property
    def format(self) -> str:
        """Return format"""
        return "%Y%m"

    def increment_date(self, current_date: datetime) -> datetime:
        if current_date.month == 12:
            return datetime(year=current_date.year + 1, month=1, day=1)
        return datetime(year=current_date.year, month=current_date.month + 1, day=1)


class HeatmapTimeframeFactory:
    """Factory class for returning heatmap timeframe instances"""

    _DEFINITIONS: Dict[str, HeatmapTimeframe] = [
        timeframe
        for timeframe in [
            HeatmapTimeframeFiveMinute(),
            HeatmapTimeframeHour(),
            HeatmapTimeframeDay(),
            HeatmapTimeframeMonth(),
        ]
    ]

    @classmethod
    def get_by_time_difference(cls, from_date, to_date):
        """Get timeframe based on time difference"""
        for instance in cls.get_all():
            if instance.enabled_for_timeframe(from_date=from_date, to_date=to_date):
                return instance

    @classmethod
    def get_all(cls):
        """Return all result timeframes"""
        return cls._DEFINITIONS

    @classmethod
    def get_by_name(cls, name):
        """Return timeframe by name"""
        for timeframe in cls._DEFINITIONS:
            if timeframe.name == name:
                return timeframe
        return None
