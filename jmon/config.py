
import os

class Config:

    _INSTANCE = None

    DATABASE_TYPE = os.environ.get("DB_TYPE")
    DATABASE_HOST = os.environ.get("DB_HOST")
    DATABASE_PORT = os.environ.get("DB_PORT")
    DATABASE_USERNAME = os.environ.get("DB_USERNAME")
    DATABASE_PASSWORD = os.environ.get("DB_PASSWORD")
    DATABASE_NAME = os.environ.get("DB_NAME")

    DEFAULT_CHECK_INTERVAL = int(os.environ.get('DEFAULT_CHECK_INTERVAL', '300'))
    MAX_CHECK_INTERVAL = int(os.environ.get('MAX_CHECK_INTERVAL', '31536000'))
    MIN_CHECK_INTERVAL = int(os.environ.get('MIN_CHECK_INTERVAL', '0'))

    DEFAULT_CHECK_TIMEOUT = int(os.environ.get('DEFAULT_CHECK_TIMEOUT', '60'))
    MAX_CHECK_TIMEOUT = int(os.environ.get('MAX_CHECK_TIMEOUT', '300'))
    MIN_CHECK_TIMEOUT = int(os.environ.get('MIN_CHECK_TIMEOUT', '1'))

    MAX_CHECK_QUEUE_TIME = int(os.environ.get('MAX_CHECK_QUEUE_TIME', 120))

    # Default to 1 week for checks to expire in UI
    UI_RESULT_EXPIRE = int(os.environ.get("UI_RESULT_EXPIRE", "604800"))

    API_KEY = os.environ.get("API_KEY")

    @property
    def DATABASE_URL(self):
        """Return database url"""
        sqlalchemy_type = None
        if self.DATABASE_TYPE == "postgresql":
            sqlalchemy_type = "postgresql+psycopg2"

        if sqlalchemy_type is None:
            raise Exception("Unrecognised DB_TYPE")

        return f"{sqlalchemy_type}://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    BROKER_TYPE = os.environ.get('BROKER_TYPE')
    BROKER_HOST = os.environ.get('BROKER_HOST')
    BROKER_USERNAME = os.environ.get('BROKER_USERNAME')
    BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD')
    BROKER_PORT = int(os.environ.get('BROKER_PORT', 0))
    BROKER_INSTANCE = os.environ.get('BROKER_INSTANCE')

    REDIS_TYPE = os.environ.get('REDIS_TYPE')
    REDIS_HOST = os.environ.get('REDIS_HOST')
    REDIS_USERNAME = os.environ.get('REDIS_USERNAME')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 0))
    REDIS_INSTANCE = os.environ.get('REDIS_INSTANCE')

    AWS_ENDPOINT = os.environ.get('AWS_ENDPOINT')
    AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')

    SCREENSHOT_ON_FAILURE_DEFAULT = os.environ.get('SCREENSHOT_ON_FAILURE_DEFAULT', 'True').lower() == 'true'

    # Set these retentions to 0 to disable.
    # Result artifact retention will replace any pre-existing S3 bucket policies - set to 0 if you are using a custom policy.
    # Default result retentions are set to 1 year
    QUEUE_TASK_RESULT_RETENTION_MINS = int(os.environ.get("QUEUE_TASK_RESULT_RETENTION", "1440"))
    RESULT_RETENTION_MINS = int(os.environ.get("RESULT_RETENTION_MINS", "525600"))
    RESULT_ARTIFACT_RETENTION_DAYS = int(os.environ.get("RESULT_ARTIFACT_RETENTION_DAYS", "365"))

    @classmethod
    def get(cls):
        """Get instance of config"""
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE
