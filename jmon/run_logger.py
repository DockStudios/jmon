
from io import StringIO
import logging

import multiprocessing

from jmon.logger import logger

class RunThreadLogFilter(logging.Filter):
    """
    This filter only show log entries for specified thread name
    """

    def __init__(self, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        # Use the billiard multiprocessing library, as this is
        # supposedly the library used by celery
        self.thread_id = multiprocessing.current_process().pid

    def filter(self, record):
        return multiprocessing.current_process().pid == self.thread_id


class RunLogger:
    """
    Handle log events for run.
    
    This is used for several reasons:
     * debug logging in a run can be captured in the run log,
       but if global log level does not mean it will be sent to
       a handler used by multiple threads (e.g. stdout), then
       the global lock does not need to be instanciated, which
       _should_ improve performance
     * loggers do not need to be created for each run.
       This class can handle the injection of run ID into logs for context,
       keeping the custom formatting contained within the class and does not
       require a custom handler for stdout with a custom formatter to inject the ID.
       It can also handle the redirection of logs for the current thread's run to
       a StreamIO to capture the logs, as without a custom logger, simulateous
       runs would log leak logs to each other, unless unique loggers were used...
       By no longer requiring custom loggers per run, this will avoid memory issues,
       as loggers are stored in the logging module globally.
    """

    should_info_debug_log = True

    @property
    def _format(self):
        """Return log format"""
        return '%(asctime)s - %(message)s'

    def __init__(self, run, enable_log):
        """Create handler, filter and store member variables"""
        self._logger = logger
        self._log_stream = StringIO()

        self._should_log = enable_log

        # Create local log handler
        self._log_handler = logging.StreamHandler(self._log_stream)
        self._log_handler.setLevel(logging.INFO)

        thread_log_filter = RunThreadLogFilter()
        self._log_handler.addFilter(thread_log_filter)

        # Add format for user-friendly logs
        formatter = logging.Formatter(self._format)
        self._log_handler.setFormatter(formatter)
        self._logger.addHandler(self._log_handler)

        self.log_prefix = ""
        # Add log handlder from root of run, if configured to log
        if self._should_log and run and run._db_run:
            self.log_prefix = f"{run._db_run.id}: "

    def _get_log_args(self, msg):
        """Get log arguments for logging"""
        return {
            "msg": f"{self.log_prefix}{msg}",
            #"extra": {'c_thread_id': multiprocessing.current_process().pid}
        }

    def cleanup(self):
        """Clean up log stream"""
        self._logger.removeHandler(self._log_handler)
        self._log_handler.flush()
        self._log_handler.close()

    def read_log_stream(self):
        """Return data from logstream"""
        # Reset log stream
        self._log_stream.seek(0)
        return self._log_stream.read()

    def debug(self, msg):
        """Debug log"""
        if self.should_info_debug_log:
            logger.debug(**self._get_log_args(msg))

    def info(self, msg):
        """Info log"""
        if self.should_info_debug_log:
            logger.info(**self._get_log_args(msg))

    def warn(self, msg):
        """Warn log"""
        logger.warn(**self._get_log_args(msg))

    def error(self, msg):
        """Error log"""
        logger.error(**self._get_log_args(msg))