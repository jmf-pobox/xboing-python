# Exception Handling, Assertions, and Input Validation

## Exception Handling

- **Always catch the most specific exception possible.**  
  Never use `except Exception:` or a bare `except:` unless absolutely necessary and justified with a comment.
- **Handle only what you can recover from.**  
  If you catch an exception, either resolve it or log and re-raise it.
- **Never silence exceptions.**  
  All caught exceptions must be logged with sufficient context for debugging.
- **Keep `try` blocks minimal.**  
  Only wrap the code that may raise the expected exception.
- **Do not use exceptions for normal control flow.**  
  Use them only for truly exceptional or error conditions.

**Example:**
```python
try:
    data = load_config(path)
except FileNotFoundError:
    logger.error(f"Config file not found: {path}")
    raise
```

## Assertions

- **Use `assert` only for internal invariants and developer errors.**
- **Never use `assert` for validating user input, file contents, or anything that can fail in production.**
- **All assertions must include a descriptive message.**

**Example:**
```python
assert x > 0, "x must be positive"
```

## Input Validation

- **Validate all external input at the boundary of your code.**
- **Use explicit checks and raise `ValueError`, `TypeError`, or custom exceptions for invalid input.**
- **Leverage type hints and static analysis tools to catch type errors.**
- **Fail fast:**  
  Validate as early as possible.

**Example:**
```python
def set_age(age: int) -> None:
    if not isinstance(age, int):
        raise TypeError("age must be an integer")
    if age < 0:
        raise ValueError("age must be non-negative")
```

## Logging

- **All exception handling blocks must log the exception with context.**
- **Use the `logging` module, not `print`.**

**Example:**
```python
try:
    ...
except ValueError as e:
    logger.error(f"Invalid value for foo: {foo!r}: {e}")
    raise
```

## Summary Table

| Situation                | What to do                                      |
|--------------------------|-------------------------------------------------|
| User/file/network input  | Validate, raise `ValueError`/`TypeError`        |
| Internal invariants      | Use `assert` with message                       |
| Expected error (file)    | Catch specific exception, log, handle/re-raise  |
| Unexpected error         | Let it propagate, or log and re-raise           |
| Never                    | Use bare `except:` or catch `Exception` broadly |

---

## References
- [PEP 8: Exceptions](https://peps.python.org/pep-0008/#programming-recommendations)
- [PEP 20: The Zen of Python](https://peps.python.org/pep-0020/)
- [Python Docs: Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Effective Python, Item 23: Use Exception Chaining Effectively](https://effectivepython.com/) 