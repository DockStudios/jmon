

class ResultTimeframe:
    """Handle properties of result timeframes"""

    def __init__(self, name, redis_key, friendly_name, ttl):
        """Store member variables"""
        self._name = name
        self._redis_key = redis_key
        self._friendly_name = friendly_name
        self._ttl = ttl

    @property
    def name(self):
        """Return name"""
        return self._name

    @property
    def redis_key(self):
        """Return redis_key"""
        return self._redis_key

    @property
    def friendly_name(self):
        """Return friendly_name"""
        return self._friendly_name

    @property
    def ttl(self):
        """Return ttl"""
        return self._ttl


class ResultTimeframeFactory:
    """Factory class for returning timeframe instances"""

    _DEFINITIONS = {
        timeframe.name
        for timeframe in [
            ResultTimeframe(name="1h", redis_key="1h", friendly_name="1 Hour", ttl=(60*60)),
            ResultTimeframe(name="6h", redis_key="6h", friendly_name="6 Hours", ttl=(6*60*60)),
            ResultTimeframe(name="12h", redis_key="12h", friendly_name="12 Hours", ttl=(12*60*60)),
            ResultTimeframe(name="1d", redis_key="1d", friendly_name="1 Day", ttl=(24*60*60)),
            ResultTimeframe(name="1w", redis_key="1w", friendly_name="1 Week", ttl=(7*24*60*60))
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
