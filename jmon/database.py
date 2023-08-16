try:
    from greenlet import getcurrent as _ident_func
except ImportError:
    from threading import get_ident as _ident_func

# from threading import get_ident as _ident_func
import sqlalchemy
import sqlalchemy.orm

import jmon.config


class Session:

    def __init__(self):
        self._thread_id = _ident_func()
        self._session = None

    def __enter__(self):
        """Create session and return"""
        self._session = sqlalchemy.orm.scoped_session(
            Database.get_session_maker()
        )
        return self._session

    def __exit__(self, *args, **kwargs):
        """Tear down session"""
        if self._session:
            self._session.close()


class Database:
    """Handle database connection and settng up database schema"""

    _ENGINE = None
    _SESSION_MAKER = None
    _SESSIONS = {}
    blob_encoding_format = 'utf-8'

    GENERAL_COLUMN_SIZE = 128
    LARGE_COLUMN_SIZE = 1024
    URL_COLUMN_SIZE = 1024

    GeneralString = sqlalchemy.String(length=GENERAL_COLUMN_SIZE)
    LargeString = sqlalchemy.String(length=LARGE_COLUMN_SIZE)
    MEDIUM_BLOB_SIZE = ((2 ** 24) - 1)

    @classmethod
    def get_engine(cls):
        """Get singleton instance of engine."""
        if cls._ENGINE is None:
            cls._ENGINE = sqlalchemy.create_engine(jmon.config.Config.get().DATABASE_URL)
        return cls._ENGINE

    @classmethod
    def get_session_maker(cls):
        """Return session local object"""
        if cls._SESSION_MAKER is None:
            cls._SESSION_MAKER = sqlalchemy.orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls.get_engine()
            )
        return cls._SESSION_MAKER

    @classmethod
    def get_session(cls):
        """Return session for the current thread"""
        thread_id = _ident_func()
        if thread_id not in cls._SESSIONS:
            cls._SESSIONS[thread_id] = sqlalchemy.orm.scoped_session(
                Database.get_session_maker()
            )
        return cls._SESSIONS[thread_id]

    @classmethod
    def clear_session(cls):
        """Clear session for thread"""
        cls.get_session().remove()

    @classmethod
    def encode_value(cls, value):
        """Encode value for binary blob"""
        if not value:
            value = ''
        return value.encode(cls.blob_encoding_format)

    @classmethod
    def decode_blob(cls, value):
        """Decode blob as a string."""
        if value is None:
            return None
        return value.decode(cls.blob_encoding_format)

Base = sqlalchemy.orm.declarative_base()
