

import datetime
from enum import Enum
import sqlalchemy
import sqlalchemy.orm

import jmon.database
import jmon.config
from jmon.step_status import StepStatus


class RunTriggerType(Enum):
    """Run trigger type"""
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class Run(jmon.database.Base):

    TIMESTAMP_FORMAT = '%Y-%m-%d_%H-%M-%S'

    @classmethod
    def get_latest_by_check(cls, check):
        """Get latest check by run"""
        session = jmon.database.Database.get_session()
        return session.query(cls).filter(cls.check==check).order_by(cls.timestamp.desc()).limit(1).first()

    @classmethod
    def get_by_check(cls, check, limit=None, trigger_type=None):
        """Get all runs by check"""
        session = jmon.database.Database.get_session()
        runs = session.query(cls).filter(cls.check==check).order_by(cls.timestamp.desc())
        if trigger_type:
            runs = runs.where(cls.trigger_type==trigger_type)
        if limit:
            runs = runs.limit(limit)
        return [run for run in runs]

    @classmethod
    def get(cls, check, timestamp_id):
        """Return run for check and timestamp"""
        session = jmon.database.Database.get_session()
        return session.query(cls).filter(cls.check==check, cls.timestamp_id==timestamp_id).first()

    @classmethod
    def create(cls, check, trigger_type):
        """Create run"""
        session = jmon.database.Database.get_session()
        run = cls(check=check)
        timestamp = datetime.datetime.now()
        run.timestamp = timestamp
        run.timestamp_id = timestamp.strftime(cls.TIMESTAMP_FORMAT)
        run.trigger_type = trigger_type

        session.add(run)
        session.commit()

        return run

    __tablename__ = 'run'

    check_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("check.id", name="fk_run_check_id_check_id"),
        nullable=False,
        primary_key=True
    )
    check = sqlalchemy.orm.relationship("Check", foreign_keys=[check_id])

    # String representation of the tiemstamp, in the format of
    # the tiemstamp_key
    timestamp_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # Datetime timestamp of check
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, primary_key=True)

    trigger_type = sqlalchemy.Column(sqlalchemy.Enum(RunTriggerType, default=RunTriggerType.SCHEDULED), nullable=False)

    status = sqlalchemy.Column(sqlalchemy.Enum(StepStatus), default=StepStatus.NOT_RUN)

    @property
    def id(self):
        """Return string representation of run"""
        return f"{self.check.name}-{self.timestamp_id}"

    def set_status(self, status):
        """Set success value"""
        session = jmon.database.Database.get_session()
        self.status = status
        session.add(self)
        session.commit()
