
import jmon.run_logger


class MockLogger(jmon.run_logger.RunLogger):

    @property
    def _format(self):
        return '%(message)s'
