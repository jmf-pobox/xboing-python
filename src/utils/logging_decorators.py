"""Logging decorators for the application."""

import functools
import logging
import time
from typing import Any, Callable, Optional, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def log_entry_exit(logger: Optional[logging.Logger] = None) -> Callable[[F], F]:
    """Log entry and exit of a function, including arguments and result.

    Args:
    ----
        logger: Optional logger to use. If None, uses self.logger or module logger.

    Returns:
    -------
        A decorator that logs entry and exit of the decorated function.

    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log = logger
            if log is None and args and hasattr(args[0], "logger"):
                log = args[0].logger
            if log is None:
                log = logging.getLogger(func.__module__)
            log.debug(f"Entering {func.__qualname__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            log.debug(f"Exiting {func.__qualname__} with result={result}")
            return result

        return cast(F, wrapper)

    return decorator


def log_exceptions(logger: Optional[logging.Logger] = None) -> Callable[[F], F]:
    """Log exceptions raised by a function.

    Args:
    ----
        logger: Optional logger to use. If None, uses self.logger or module logger.

    Returns:
    -------
        A decorator that logs exceptions raised by the decorated function.

    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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

        return cast(F, wrapper)

    return decorator


def log_timing(logger: Optional[logging.Logger] = None) -> Callable[[F], F]:
    """Log the execution time of a function.

    Args:
    ----
        logger: Optional logger to use. If None, uses self.logger or module logger.

    Returns:
    -------
        A decorator that logs the execution time of the decorated function.

    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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

        return cast(F, wrapper)

    return decorator
