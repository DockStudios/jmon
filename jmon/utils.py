

from enum import Enum
from time import sleep

from jmon.logger import logger


# Unset object, for handling default values
# for optional arguments
UNSET = object()


class RetryStatus(Enum):
    """Retry return status enum"""
    ONLY_IF_CONDITION_FAILURE = "ONLY_IF_CONDITION_FAILURE"


def retry(count, interval):
    def wrapper(func):
        def execute_attempt(*args, only_if=None, **kwargs):
            res = None
            for itx in range(count):
                # Use callback only_if method to
                # determine if the retry should run
                if only_if is not None:
                    if not only_if():
                        return RetryStatus.ONLY_IF_CONDITION_FAILURE

                res = func(*args, **kwargs)
                if res is not None:
                    return res
                else:
                    sleep(interval)
                    logger.error(f"Retrying step ({itx + 1}/{count})")
            else:
                return res

        return execute_attempt
    return wrapper
