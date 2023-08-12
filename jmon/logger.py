
from io import StringIO
import logging

logger = logging.getLogger(__name__)


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

    def __init__(self, run):
        """Store run and create log stream"""
        self._run = run
        self._log_stream = StringIO()

        # Create local log handler
        self._log_handler = logging.StreamHandler(self._log_stream)
        self._log_handler.setLevel(logging.DEBUG)

        # Add format for user-friendly logs
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        self._log_handler.setFormatter(formatter)
        #self._logger.addHandler(self._log_handler)

        # Add log handlder from root of run, if configured to log
        # if self._should_log and self._run:
        #     self._logger.addHandler(self._run.log_handler)

    def debug(self, msg, *args):
        """Handle debug log"""
        record = logger.makeRecord(name=self._run.id, level=logging.DEBUG, fn=None, lno=None, msg=msg, args=args, exc_info=None)
        self._log_handler.handle(record)
        logger.debug(msg)

    def info(self, msg, *args):
        """Handle debug log"""
        record = logger.makeRecord(name=self._run.id, level=logging.INFO, fn=None, lno=None, msg=msg, args=args, exc_info=None)
        print(record)
        self._log_handler.handle(record)
        logger.info(msg)


# class TestRun:
#     id = "logger"
# test = RunLogger(run=TestRun())
# test.info("test")
# test._log_handler.flush()
# print(test._log_stream.read())