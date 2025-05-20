import logging
import time
from ..Log.logging_config import setup_logger
setup_logger()


def retry_until_success(func, max_retries, delay=2, exceptions=(Exception,), on_fail_message=None, on_fail_execute_message=None):
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions:
            logging.info(f"{on_fail_message or 'Attempt failed'}, retrying... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
    raise Exception(on_fail_execute_message or "Max retries exceeded")

def retryable(max_retries=3, delay=2, exceptions=(Exception,), on_fail_message="", on_fail_execute_message=""):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return retry_until_success(
                func=lambda: func(*args, **kwargs),
                max_retries=max_retries,
                delay=delay,
                exceptions=exceptions,
                on_fail_message=on_fail_message,
                on_fail_execute_message=on_fail_execute_message
            )
        return wrapper
    return decorator