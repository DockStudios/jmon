

from datetime import datetime, timedelta


class ResultTimeframe:
    """Handle properties of result timeframes"""

    def __init__(self, name, hours, friendly_name):
        """Store member variables"""
        self._name = name
        self._hours = hours
        self._friendly_name = friendly_name

    @property
    def name(self):
        """Return name"""
        return self._name

    @property
    def hours(self):
        """Return hours"""
        return self._hours

    @property
    def friendly_name(self):
        """Return friendly_name"""
        return self._friendly_name

    def get_from_timestamp(self):
        """Return 'from' timestamp"""
        return datetime.now() - timedelta(hours=self.hours)


class ResultTimeframeFactory:
    """Factory class for returning timeframe instances"""

    _DEFINITIONS = {
        timeframe.name: timeframe
        for timeframe in [
            ResultTimeframe(name="1h", hours=1, friendly_name="1 Hour"),
            ResultTimeframe(name="6h", hours=6, friendly_name="6 Hours"),
            ResultTimeframe(name="12h", hours=12, friendly_name="12 Hours"),
            ResultTimeframe(name="1d", hours=24, friendly_name="1 Day"),
            ResultTimeframe(name="1w", hours=(24*7), friendly_name="1 Week"),
            ResultTimeframe(name="4w", hours=(24*7*4), friendly_name="4 Weeks")
        ]
    }

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
