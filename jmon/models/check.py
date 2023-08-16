

import sqlalchemy

from redbeat import RedBeatSchedulerEntry
import yaml
import json
import celery
import celery.schedules

from jmon.client_type import ClientType
from jmon import app
import jmon.database
import jmon.config
from jmon.errors import CheckCreateError, StepValidationError
import jmon.models
from jmon.steps.root_step import RootStep
import jmon.run
from jmon.logger import logger


class Check(jmon.database.Base):

    @classmethod
    def get_all(cls):
        """Get all checks"""
        session = jmon.database.Database.get_session()
        return session.query(cls).all()

    @classmethod
    def get_by_environment(cls, environment):
        """Get all checks by environment"""
        session = jmon.database.Database.get_session()
        return session.query(cls).filter(cls.environment==environment)

    @classmethod
    def get_by_name_and_environment(cls, name, environment):
        """Get all checks"""
        session = jmon.database.Database.get_session()
        return session.query(cls).filter(cls.name==name, cls.environment==environment).first()

    @classmethod
    def from_yaml(cls, yml):
        """Return instance of class from check yaml"""
        try:
            content = yaml.safe_load(yml)
        except Exception as exc:
            raise CheckCreateError('Invalid YAML')

        if type(content) is not dict:
            raise CheckCreateError("YAML must be a dictionary")

        if not (name := content.get("name")):
            raise CheckCreateError("No name defined for check")

        if not (steps := content.get("steps")):
            raise CheckCreateError("No steps defined for check")

        # Check for existing steps with the same name
        session = jmon.database.Database.get_session()

        environment = None
        # If an environment has been provided, ensure it exists
        if environment_name := content.get("environment"):
            environment = jmon.models.environment.Environment.get_by_name(environment_name)
            if environment is None:
                raise CheckCreateError(f"Environment does not exist: {environment_name}")

        # If an environment has not been provided, determine
        # if a single environment has been defined, and use that
        else:
            environments = jmon.models.environment.Environment.get_all()
            if len(environments) == 1:
                environment = environments[0]
            else:
                raise CheckCreateError(
                    "Environment must be defined - "
                    "this can only be ommited if a single environment exists"
                )

        instance = cls.get_by_name_and_environment(name=name, environment=environment)
        # Create new instance of check, if it doesn't exist
        if not instance:
            instance = cls(name=name, environment=environment)

        instance.steps = steps
        instance.screenshot_on_error = content.get("screenshot_on_error")

        # If a client type has been provided, convert to enum,
        # hanlding invalid values
        if client_type := content.get("client"):
            try:
                instance.client = ClientType(client_type)
            except ValueError:
                raise CheckCreateError("Invalid client type")
        else:
            instance.client = None
        instance.interval = int(content.get("interval", 0))
        instance.timeout = int(content.get("timeout", 0))

        # Create root step and perform check to ensure
        # steps are valid
        try:
            root_step = RootStep(run=None, config=instance.steps, parent=None)
            root_step.validate_steps()
        except StepValidationError as exc:
            raise CheckCreateError(str(exc))

        # Add custom attributes
        content_attributes = content.get("attributes", {})
        if type(content_attributes) is not dict:
            raise CheckCreateError("attributes must be a map of key-value pairs")
        instance.attributes = content_attributes

        session.add(instance)
        session.commit()

        # Enable check by default, or if directed to
        if content.get("enable", True):
            instance.enable()
        else:
            instance.disable()

        return instance


    __tablename__ = 'check'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(jmon.database.Database.GeneralString, nullable=False)
    screenshot_on_error = sqlalchemy.Column(sqlalchemy.Boolean)
    interval = sqlalchemy.Column(sqlalchemy.Integer)
    timeout = sqlalchemy.Column(sqlalchemy.Integer)
    client = sqlalchemy.Column(sqlalchemy.Enum(ClientType), default=None)
    _steps = sqlalchemy.Column(
        sqlalchemy.LargeBinary(
            length=jmon.database.Database.MEDIUM_BLOB_SIZE
        ),
        name="steps_b"
    )
    _enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True, name="enabled")
    _attributes = sqlalchemy.Column(
        sqlalchemy.LargeBinary(
            length=jmon.database.Database.MEDIUM_BLOB_SIZE
        ),
        name="attributes_b"
    )

    environment_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey("environment.id", name="fk_check_environment_id_environment_id"),
        nullable=True,

    )
    environment = sqlalchemy.orm.relationship("Environment", foreign_keys=[environment_id])

    # Add unique contraint across name and environment ID
    __table_args__ = (sqlalchemy.UniqueConstraint('name', 'environment_id', name='uc_name_environment_id'), )

    @property
    def steps(self):
        """Return steps dictionary"""
        return json.loads(self._steps.decode('utf-8'))

    @steps.setter
    def steps(self, value):
        """Set steps in database"""
        self._steps = json.dumps(value).encode('utf-8')

    @property
    def attributes(self):
        """Return attributes dictionary"""
        if self._attributes:
            return json.loads(self._attributes.decode('utf-8'))
        return {}

    @attributes.setter
    def attributes(self, value):
        """Set attributes column value"""
        self._attributes = (json.dumps(value) if value else "{}").encode('utf-8')

    @property
    def should_screenshot_on_error(self):
        """Whether a screenshot should be taken on error"""
        # Return confinguration for check, if available
        if self.screenshot_on_error is not None:
            return self.screenshot_on_error

        # Return default config for whether to screenshot on failure
        return jmon.config.Config.get().SCREENSHOT_ON_FAILURE_DEFAULT

    @property
    def enabled(self):
        """Return whether check is enabled, default empty column to True"""
        return self._enabled is not False

    @enabled.setter
    def enabled(self, value):
        """Set enabled flag"""
        self._enabled = value

    def get_step_count(self):
        """Get number of steps"""
        def get_all_steps(parent):
            children = parent.get_child_steps()
            steps = children
            for child in children:
                steps += get_all_steps(child)
            return steps

        root_step = RootStep(run=jmon.run.Run(check=self), config=self.steps, parent=None)
        steps = get_all_steps(root_step)
        return len(steps)

    def delete(self):
        """Delete check"""
        # Delete schedule
        self.delete_schedule()

        # Delete runs
        session = jmon.database.Database.get_session()
        session.query(
            jmon.models.run.Run
        ).filter(
            jmon.models.run.Run.check==self
        ).delete()

        # Delete from database
        session.delete(self)
        session.commit()

    def enable(self):
        """Enable the check"""
        # Update DB row
        session = jmon.database.Database.get_session()
        self.enabled = True
        session.add(self)
        session.commit()

        self.upsert_schedule()

    def disable(self):
        """Disable the check"""
        self.delete_schedule()

        # Update DB row
        session = jmon.database.Database.get_session()
        self.enabled = False
        session.add(self)
        session.commit()

    @property
    def schedule_key(self):
        """Return schedule key, as registered with redbeat"""
        return f'check_{self.name}_{self.environment.name}'

    @property
    def redis_schedule_key(self):
        """Return internal schedule key used in redis"""
        return f'redbeat:{self.schedule_key}'

    def upsert_schedule(self):
        """Register or update schedule"""
        options = self.task_options
        if not options:
            return

        interval_seconds = self.get_interval()
        interval = celery.schedules.schedule(run_every=interval_seconds)

        needs_to_save = False
        try:
            entry = RedBeatSchedulerEntry.from_key(key=self.redis_schedule_key, app=app)
            logger.debug("Found existing schedule for task")
            if (entry.schedule.run_every != interval.run_every or
                    entry.options.get('headers') != options['headers'] or
                    entry.options.get('exchange') != options['exchange'] or
                    entry.options.get('exchange_type') != options['exchange_type'] or
                    entry.options.get('expires') != options['expires']):
                # Update interval and set directive to save
                logger.debug(f"Header match: {entry.options.get('headers') == options['headers']}: {entry.options.get('headers')}, {options['headers']}")
                logger.debug(f"Exchange match: {entry.options.get('exchange') == options['exchange']}: {entry.options.get('exchange')}, {options['exchange']}")
                logger.debug(f"Schedule entry match: {entry.schedule.run_every == interval.run_every}: {entry.schedule.run_every}, {interval.run_every}")
                logger.debug(f"Schedule entry match: {entry.options.get('expires') == options['expires']}: {entry.options.get('expires')}, {options['expires']}")
                logger.debug("Interval/options need updating")
                entry.schedule.run_every = interval.run_every
                entry.options.update(options)

                needs_to_save = True

        except KeyError:
            # If it does not exist, create new entry
            logger.debug("Schedule does not exist.. creating new entry")
            entry = RedBeatSchedulerEntry(
                self.schedule_key,
                'jmon.tasks.perform_check.perform_check',
                interval,
                args=[self.name, self.environment.name],
                app=app,
                options=options
            )
            needs_to_save = True

        if needs_to_save:
            logger.info(f"Saving schedule/re-scheduling: {self.schedule_key}")
            entry.save()
            entry.reschedule()

        return needs_to_save

    def delete_schedule(self):
        """De-register from schedule"""
        # Delete from schedule, if it exists
        try:
            entry = RedBeatSchedulerEntry.from_key(key=self.redis_schedule_key, app=app)
            entry.delete()
            return True
        except KeyError:
            logger.warn("Schedule could not be found during deletion")
            return False

    def get_result_key(self):
        """Get redis key prefix for results."""
        return f"jmon_run_result_{self.name}_"

    def get_interval(self):
        """Return interval of check, based on custom definition, global min/max and default interval"""
        config = jmon.config.Config.get()
        # If the interval has been set on the check
        if self.interval:
            return max(min(self.interval, config.MAX_CHECK_INTERVAL), config.MIN_CHECK_INTERVAL)

        # Return default check interval
        return config.DEFAULT_CHECK_INTERVAL

    def get_timeout(self):
        """Return timout of check, based on custom definition, global min/max and default interval"""
        config = jmon.config.Config.get()
        # If the timeout has been set on the check
        if self.timeout:
            return max(min(self.timeout, config.MAX_CHECK_TIMEOUT), config.MIN_CHECK_TIMEOUT)

        # Return default check timeout
        return config.DEFAULT_CHECK_TIMEOUT

    def get_supported_clients(self):
        """Get supported clients"""
        supported_clients = ClientType.get_all()
        if self.client:
            supported_clients = [self.client]

        root_step = RootStep(run=jmon.run.Run(check=self), config=self.steps, parent=None)

        supported_clients = root_step.get_supported_clients(supported_clients)
        return supported_clients

    @property
    def task_headers(self):
        """Get queue for task"""
        supported_clients = self.get_supported_clients()

        if not supported_clients:
            logger.warn(f"Check does not have any compatible client types: {self.name}")
            return None

        headers = {}

        if ClientType.REQUESTS in supported_clients:
            headers["requests"] = "true"
        if ClientType.BROWSER_CHROME in supported_clients:
            headers["chrome"] = "true"
        if ClientType.BROWSER_FIREFOX in supported_clients:
            headers["firefox"] = "true"
        return headers

    @property
    def task_options(self):
        """Return options for task"""
        headers = self.task_headers
        if not headers:
            return

        return {
            'headers': headers,
            'exchange': 'check',
            "exchange_type": "headers",
            "expires": jmon.config.Config.get().MAX_CHECK_QUEUE_TIME
        }
