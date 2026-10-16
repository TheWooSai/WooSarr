"""Retry decorator with exponential backoff."""

import time
import functools
from typing import Callable, Type, Tuple, Optional


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """Decorator that retries a function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts before giving up.
        backoff_factor: Multiplier for backoff time (seconds).
        exceptions: Tuple of exception types to retry on.
        on_retry: Optional callback called on each retry with (attempt, exception).
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        wait_time = backoff_factor * (2 ** (attempt - 1))
                        if on_retry:
                            on_retry(attempt, e)
                        time.sleep(wait_time)
                    else:
                        raise
            raise last_exception
        return wrapper
    return decorator