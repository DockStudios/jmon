
from enum import Enum
import os
from typing import Optional


class ChromeHeadlessMode(Enum):
    """Type of headless mode to use for chrome"""
    # Disable headless mode
    NONE = "None"
    # "New" chrome headless mode - this is a newer method, but appears to be slower
    NEW = "New"
    # Legacy chrome headless mode - this appears to be the fastest method
    LEGACY = "Legacy"


class Config:

    _INSTANCE: Optional['Config'] = None

    @property
    def DATABASE_TYPE(self) -> Optional[str]:
        """Database type - currently only 'postgresql' is supported"""
        return os.environ.get("DB_TYPE")

    @property
    def DATABASE_HOST(self) -> Optional[str]:
        """Database hostname/IP"""
        return os.environ.get("DB_HOST")

    @property
    def DATABASE_PORT(self) -> Optional[str]:
        """Database port"""
        return os.environ.get("DB_PORT")

    @property
    def DATABASE_USERNAME(self) -> Optional[str]:
        """Database username"""
        return os.environ.get("DB_USERNAME")

    @property
    def DATABASE_PASSWORD(self) -> Optional[str]:
        """Database password"""
        return os.environ.get("DB_PASSWORD")

    @property
    def DATABASE_NAME(self) -> Optional[str]:
        """Database DB name"""
        return os.environ.get("DB_NAME")

    @property
    def DEFAULT_CHECK_INTERVAL(self) -> int:
        """Default check run interval, if not specified by check (seconds)"""
        return int(os.environ.get('DEFAULT_CHECK_INTERVAL', '300'))

    @property
    def MAX_CHECK_INTERVAL(self) -> int:
        """Max check run interval"""
        return int(os.environ.get('MAX_CHECK_INTERVAL', '31536000'))

    @property
    def MIN_CHECK_INTERVAL(self) -> int:
        """Min check run interval"""
        return int(os.environ.get('MIN_CHECK_INTERVAL', '0'))

    @property
    def DEFAULT_CHECK_TIMEOUT(self) -> int:
        """Default run timeout"""
        return int(os.environ.get('DEFAULT_CHECK_TIMEOUT', '60'))

    @property
    def MAX_CHECK_TIMEOUT(self) -> int:
        """Max run timeout"""
        return int(os.environ.get('MAX_CHECK_TIMEOUT', '300'))

    @property
    def MIN_CHECK_TIMEOUT(self) -> int:
        """Min run timeout"""
        return int(os.environ.get('MIN_CHECK_TIMEOUT', '1'))

    @property
    def MAX_CHECK_QUEUE_TIME(self) -> int:
        """Check queue timeout"""
        return int(os.environ.get('MAX_CHECK_QUEUE_TIME', 120))

    # Default to 1 week for checks to expire in UI
    @property
    def UI_RESULT_EXPIRE(self):
        return int(os.environ.get("UI_RESULT_EXPIRE", "604800"))

    @property
    def API_KEY(self) -> Optional[str]:
        """
        API key

        Default unset, allowing unauthenticated access to APIs
        """
        return os.environ.get("API_KEY")

    @property
    def CHECK_CRITICAL_THRESHOLD(self) -> float:
        """Threshold for warning->critical check status in UI"""
        return float(os.environ.get("CHECK_CRITICAL_THRESHOLD", "99.0"))

    @property
    def CHECK_WARNING_THRESHOLD(self) -> float:
        """Threshold for okay->warning check status in UI"""
        return float(os.environ.get("CHECK_WARNING_THRESHOLD", "99.9"))

    @property
    def DATABASE_URL(self) -> str:
        """Return database url"""
        sqlalchemy_type = None
        if self.DATABASE_TYPE == "postgresql":
            sqlalchemy_type = "postgresql+psycopg2"

        if sqlalchemy_type is None:
            raise Exception("Unrecognised DB_TYPE")

        return f"{sqlalchemy_type}://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def BROKER_TYPE(self) -> str:
        """Configure type of broker. Currently only supports 'amqp'"""
        return os.environ.get('BROKER_TYPE', 'amqp')

    @property
    def BROKER_HOST(self) -> Optional[str]:
        """Broker hostname/ip"""
        return os.environ.get('BROKER_HOST')

    @property
    def BROKER_USERNAME(self) -> Optional[str]:
        """Broker username"""
        return os.environ.get('BROKER_USERNAME')

    @property
    def BROKER_PASSWORD(self) -> Optional[str]:
        """Broker password"""
        return os.environ.get('BROKER_PASSWORD')

    @property
    def BROKER_PORT(self) -> int:
        """Broker port"""
        return int(os.environ.get('BROKER_PORT', 0))

    @property
    def BROKER_INSTANCE(self) -> Optional[str]:
        """Broker vhost"""
        return os.environ.get('BROKER_INSTANCE')

    @property
    def REDIS_TYPE(self) -> Optional[str]:
        """Redis type - currently only supports 'redis'"""
        return os.environ.get('REDIS_TYPE')

    @property
    def REDIS_HOST(self) -> Optional[str]:
        """Redis hostname/IP"""
        return os.environ.get('REDIS_HOST')

    @property
    def REDIS_USERNAME(self) -> Optional[str]:
        """Redis username"""
        return os.environ.get('REDIS_USERNAME')

    @property
    def REDIS_PASSWORD(self) -> Optional[str]:
        """Redis password"""
        return os.environ.get('REDIS_PASSWORD')

    @property
    def REDIS_PORT(self) -> int:
        """Redis port"""
        return int(os.environ.get('REDIS_PORT', 0))

    @property
    def REDIS_INSTANCE(self) -> Optional[str]:
        """Redis instance ID"""
        return os.environ.get('REDIS_INSTANCE')

    @property
    def VICTORIAMETRICS_URL(self) -> Optional[str]:
        """Victoriametrics URL"""
        return os.environ.get("VICTORIAMETRICS_URL")

    @property
    def CACHE_BROWSER(self) -> bool:
        """
        Whether to cache browser between runs.

        This is experimental and might be unstable.

        Use on non-production environment
        """
        return os.environ.get("CACHE_BROWSER", "False") == "True"

    @property
    def PREFER_CACHED_BROWSER(self) -> bool:
        """
        Whether the order of browser preference can be changed
        to use a cached browser.

        If a check supports Firefox and Chrome, firefox is used by default.

        However, if an agent has a Chrome browser cached, enabling this option
        will cause the run to switch to use Chrome, which will improve
        run startup performance.

        This may result in inconsistent browsers across runs, where a check is run
        with one type of browser and a different on the next.
        """
        return os.environ.get("PREFER_CACHED_BROWSER", "True") == "True"

    @property
    def CHROME_HEADLESS_MODE(self) -> ChromeHeadlessMode:
        """Chrome headless mode. Options: None, New or Legacy"""
        return ChromeHeadlessMode(os.environ.get("CHROME_HEADLESS_MODE", "Legacy"))

    @property
    def FIREFOX_HEADLESS(self) -> bool:
        """Whether to run firefox in headless mode"""
        return os.environ.get("FIREFOX_HEADLESS", "True") == "True"

    @property
    def AWS_ENDPOINT(self) -> Optional[str]:
        """HTTPS url for AWS ENDPOINT for accessing S3. Set to minio API URL, if in use."""
        return os.environ.get('AWS_ENDPOINT')

    @property
    def AWS_BUCKET_NAME(self) -> Optional[str]:
        """Name of s3 bucket for storing artifacts"""
        return os.environ.get('AWS_BUCKET_NAME')

    @property
    def SCREENSHOT_ON_FAILURE_DEFAULT(self) -> bool:
        """Whether to always perform a screenshot after a run in browser tests"""
        return os.environ.get('SCREENSHOT_ON_FAILURE_DEFAULT', 'True').lower() == 'true'

    @property
    def QUEUE_TASK_RESULT_RETENTION_MINS(self) -> int:
        """Expiry time for celary task results from redis"""
        return int(os.environ.get("QUEUE_TASK_RESULT_RETENTION", "1440"))

    @property
    def RESULT_RETENTION_MINS(self) -> int:
        """
        Expiry time of run results from database (in minutes).

        Defaults to `RESULT_ARTIFACT_RETENTION_DAYS` (converted to minutes).

        This should generally be configured to the same period of time as RESULT_ARTIFACT_RETENTION_DAYS.
        """
        return int(os.environ.get("RESULT_RETENTION_MINS", self.RESULT_ARTIFACT_RETENTION_DAYS * 24 * 60))

    @property
    def RESULT_ARTIFACT_RETENTION_DAYS(self) -> int:
        """
        Result artifact retention, containing logs and screenshots. This will replace any pre-existing S3 bucket policies.

        Set to 0 if you are using a custom policy or do no want artifacts to be deleted.
        """
        return int(os.environ.get("RESULT_ARTIFACT_RETENTION_DAYS", "365"))

    @property
    def SENTRY_DSN(self) -> Optional[str]:
        """Sentry DSN to enable error reporting to sentry"""
        return os.environ.get("SENTRY_DSN")

    @property
    def SENTRY_ENVIRONMENT(self) -> str:
        """Sentry environment"""
        return os.environ.get("SENTRY_ENVIRONMENT", "prod")

    @classmethod
    def get(cls) -> 'Config':
        """Get instance of config"""
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE
