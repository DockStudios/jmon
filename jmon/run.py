

import datetime
from io import StringIO
import logging
import os
from typing import Optional

from jmon.logger import logger
from jmon.artifact_storage import ArtifactStorage
from jmon.run_step_data import RunStepData
from jmon.plugins import NotificationLoader
import jmon.result_database
import jmon.models.run
from jmon.run_logger import RunLogger
from jmon.step_status import StepStatus
from jmon.steps.root_step import RootStep
import jmon.timeseries_database
import jmon.config


class Run:

    def __init__(self, check, db_run=None):
        """Store run information"""
        self._check = check
        self._db_run = db_run

        self._artifact_paths = []

        self._logger = RunLogger(run=self, enable_log=True)
        self._root_step = RootStep(run=self, config=self.check.steps, parent=None, run_logger=self._logger)
        self._start_time: Optional[datetime.datetime] = None
        self._end_time: Optional[datetime.datetime] = None
        self._variables = {}

    @property
    def run_model(self):
        """Return run model"""
        return self._db_run

    @property
    def execution_time(self) -> float:
        """Return execution time in seconds"""
        if self._start_time is None or self._end_time is None:
            return None
        return (self._end_time - self._start_time).total_seconds()

    @property
    def variables(self):
        """Return runtime variables"""
        return self._variables

    def set_variable(self, key, value):
        """Set runtime variable"""
        self._variables[key] = value

    @property
    def logger(self):
        """Return logger"""
        if self._logger is None:
            raise Exception("Attempt to access run logger before start() called")
        return self._logger

    @property
    def root_step(self):
        """Return root step instance"""
        return self._root_step

    def start(self, trigger_type):
        """Start run, setting up db run object and logging"""
        if self._db_run is not None:
            raise Exception("Cannot start run with Run DB modal already configured")
        self._db_run = jmon.models.run.Run.create(check=self._check, trigger_type=trigger_type)

    @property
    def check(self):
        """Return check"""
        return self._check

    @property
    def success(self):
        """Return success status"""
        return self._db_run.status == StepStatus.SUCCESS

    def register_artifact(self, path):
        """Register artifact to be uploaded to artifact storage"""
        self._artifact_paths.append(path)

    def get_stored_artifacts(self):
        """Get list of artifacts from storage"""
        artifact_storage = ArtifactStorage()
        artifact_prefix = f"{self.get_artifact_key()}/"
        return [
            key.replace(artifact_prefix, '')
            for key in artifact_storage.list_files(artifact_prefix)
        ]

    def get_artifact_content(self, artifact):
        """Get artifact content"""
        artifact_storage = ArtifactStorage()
        artifact_path = f"{self.get_artifact_key()}/{artifact}"
        return artifact_storage.get_file(artifact_path)

    def end(self, run_status):
        """End logging and upload"""
        self._end_time = datetime.datetime.now()
        self._db_run.set_status(run_status)

        self.logger.cleanup()

        # Upload to storage
        artifact_storage = ArtifactStorage()
        RunStepData(artifact_storage=artifact_storage, run=self).upload_file()
        artifact_storage.upload_file(f"{self.get_artifact_key()}/artifact.log", content=self.logger.read_log_stream())
        artifact_storage.upload_file(f"{self.get_artifact_key()}/status", content=self._db_run.status.value)
        for artifact_path in self._artifact_paths:
            _, artifact_name = os.path.split(artifact_path)
            artifact_storage.upload_file(f"{self.get_artifact_key()}/{artifact_name}", source_path=artifact_path)

        if self._db_run.trigger_type is jmon.models.run.RunTriggerType.SCHEDULED:
            # Create metrics for scheduled runs
            result_database = jmon.result_database.ResultDatabase()
            latest_status_metric = jmon.result_database.ResultMetricLatestStatus()
            latest_status_metric.write(result_database=result_database, run=self)

            # Write victoria metrics
            victoria_metrics = jmon.timeseries_database.VictoriaMetricsDatabase(
                url=jmon.config.Config.get().VICTORIAMETRICS_URL
            )
            run_result_metric = jmon.timeseries_database.RunResultMetricWriter()
            run_result_metric.write(result_database=victoria_metrics, run=self)

            # Send notifications using plugins
            self.send_notifications(run_status)

    def send_notifications(self, run_status):
        """Send notifications to plugins"""
        methods_to_call = [
            # Always call the "on_complete" method
            "on_complete"
        ]

        last_2_runs = jmon.models.run.Run.get_by_check(check=self._check, limit=2)
        is_new_state = False
        # If this is the first run, count as a state change
        if len(last_2_runs) == 1:
            is_new_state = True
        # Otherwise, set is_new_state if last two runs had differing results
        elif last_2_runs[0].status != last_2_runs[1].status:
            is_new_state = True

        # Create list of methods to be called on the notification plugin
        if run_status is StepStatus.SUCCESS:
            methods_to_call.append("on_every_success")
            if is_new_state:
                methods_to_call.append("on_first_success")
        elif run_status is StepStatus.FAILED:
            methods_to_call.append("on_every_failure")
            if is_new_state:
                methods_to_call.append("on_first_failure")

        elif run_status is StepStatus.TIMEOUT:
            methods_to_call.append("on_every_timeout")
            if is_new_state:
                methods_to_call.append("on_first_timeout")

        for notification_plugin in NotificationLoader.get_instance().get_plugins():
            logger.debug(f"Processing notification plugin: {notification_plugin}")
            for method_to_call in methods_to_call:
                try:
                    logger.debug(f"Calling notification plugin method: {notification_plugin}.{method_to_call}")
                    getattr(notification_plugin(), method_to_call)(
                        check_name=self._check.name,
                        run_status=run_status,
                        environment_name=self._check.environment.name,
                        run_timestamp=self._db_run.timestamp_id,
                        run_log=self.logger.read_log_stream(),
                        attributes=self.check.attributes
                    )
                except Exception as exc:
                    logger.warn(f"Failed to call notification method: {str(exc)}")

    def get_run_key(self):
        """Return datetime key for run"""
        return self._db_run.timestamp_id

    def get_artifact_key(self):
        """Return key for run"""
        return f"{self._check.name}/{self._check.environment.name}/{self.get_run_key()}"

    def start_timer(self):
        """Set start time of run"""
        self._start_time = datetime.datetime.now()

    def get_remaining_time(self):
        """Get remaining time between start time of run and timeout"""
        return (
            (self._start_time + datetime.timedelta(seconds=self.check.get_timeout())) -
            datetime.datetime.now()
        )
