"""
Retry module: provides a retry decorator with exponential backoff for API calls.
"""

import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_with_backoff(retries=3, base_delay=1.0):
    """
    Retry decorator with exponential backoff.
    Attempts `retries` times, backing off: base_delay * (2 ** attempt).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= retries:
                        logger.error(f"Function '{func.__name__}' failed after {retries} attempts. Final error: {e}")
                        raise RuntimeError(f"Operation failed after {retries} attempts: {str(e)}") from e
                    
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Transient error in '{func.__name__}': {e}. "
                        f"Retrying in {delay}s... (Attempt {attempt}/{retries - 1})"
                    )
                    time.sleep(delay)
        return wrapper
    return decorator
