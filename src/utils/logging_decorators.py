import functools
import logging
import time


def log_entry_exit(logger=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use self.logger if available
            log = logger
            if log is None and args and hasattr(args[0], "logger"):
                log = args[0].logger
            if log is None:
                log = logging.getLogger(func.__module__)
            log.debug(f"Entering {func.__qualname__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            log.debug(f"Exiting {func.__qualname__} with result={result}")
            return result

        return wrapper

    return decorator


def log_exceptions(logger=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = logger
            if log is None and args and hasattr(args[0], "logger"):
                log = args[0].logger
            if log is None:
                log = logging.getLogger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.exception(f"Exception in {func.__qualname__}: {e}")
                raise

        return wrapper

    return decorator


def log_timing(logger=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = logger
            if log is None and args and hasattr(args[0], "logger"):
                log = args[0].logger
            if log is None:
                log = logging.getLogger(func.__module__)
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            log.debug(f"{func.__qualname__} took {elapsed:.3f}s")
            return result

        return wrapper

    return decorator
