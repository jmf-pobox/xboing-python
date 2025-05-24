# LOGGING-DESIGN.md

## Overview

This document describes the logging design for the XBoing Python project. The goal is to provide a robust, flexible, and unobtrusive logging system that:

- Centralizes logging configuration (log level, format, handlers) in a single place.
- Defaults to logging to a file (not stdout), with optional console output for development.
- Allows per-class or per-module log level overrides.
- Encourages the use of Python decorators for logging entry/exit, exceptions, and timing, to avoid code clutter.
- Follows Python logging best practices for maintainability and testability.

---

## 1. Centralized Logging Configuration

- **Location:** All logging configuration should be performed in a single module, e.g., `src/utils/logging_config.py`.
- **Initialization:** The main entry point (`main.py`) should import and initialize logging from this module before any other imports that use logging.
- **Log File:** The default log file is `game_debug.log` at the project root.
- **Log Level:** The default log level (e.g., `INFO` or `DEBUG`) is set in `logging_config.py` and can be overridden via environment variable or config file.
- **Format:** Use a consistent, informative log format including timestamp, level, logger name, and message.

### Example (`logging_config.py`):

```python
import logging
import os

def setup_logging(default_level=logging.INFO, log_file="game_debug.log"):
    log_level = os.getenv("XBOING_LOGLEVEL", default_level)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w"),
            # Uncomment the next line for optional console output
            # logging.StreamHandler()
        ],
    )
```

---

## 2. Logger Usage in Code

- **Naming:** Use `logging.getLogger(__name__)` for module-level loggers, or `logging.getLogger(f"xboing.{ClassName}")` for class-specific loggers.
- **Per-Class/Module Level:** Override log level for a specific logger using `logger.setLevel(logging.DEBUG)` as needed.
- **No Print Statements:** Use logging for all runtime diagnostics, warnings, and errors.

---

## 3. Logging Decorators

To reduce code clutter, use decorators for common logging patterns:

- **@log_entry_exit:** Logs function entry and exit, including arguments and return values.
- **@log_exceptions:** Logs exceptions raised in the decorated function.
- **@log_timing:** Logs execution time of the decorated function.

### Example (`logging_decorators.py`):

```python
import functools
import logging
import time

def log_entry_exit(logger=None):
    def decorator(func):
        log = logger or logging.getLogger(func.__module__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log.debug(f"Entering {func.__name__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            log.debug(f"Exiting {func.__name__} with result={result}")
            return result
        return wrapper
    return decorator

def log_exceptions(logger=None):
    def decorator(func):
        log = logger or logging.getLogger(func.__module__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.exception(f"Exception in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

def log_timing(logger=None):
    def decorator(func):
        log = logger or logging.getLogger(func.__module__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            log.debug(f"{func.__name__} took {elapsed:.3f}s")
            return result
        return wrapper
    return decorator
```

---

## 4. Best Practices

- **Configuration First:** Always configure logging before importing modules that use it.
- **Granular Loggers:** Use module or class-specific loggers for fine-grained control.
- **Log Levels:** Use appropriate log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- **Testing:** Use `caplog` in tests to assert on log output.
- **No Global State:** Avoid global logger state; always get loggers by name.
- **Documentation:** Document any custom logging behavior in this file.

---

## 5. Example Usage

```python
from utils.logging_config import setup_logging
from utils.logging_decorators import log_entry_exit, log_exceptions

setup_logging()

import logging
logger = logging.getLogger(__name__)

@log_entry_exit(logger)
@log_exceptions(logger)
def do_something(x, y):
    return x + y

class MyClass:
    def __init__(self):
        self.logger = logging.getLogger(f"xboing.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)  # Override if needed

    @log_entry_exit()
    def my_method(self):
        self.logger.info("Doing something important")
```

---

## 6. Extending and Maintaining

- Add new decorators for common patterns as needed.
- Update this document and `logging_config.py` if logging requirements change.
- Review log output regularly to ensure it is useful and not overly verbose. 