"""Stage 0 exercise: decorators and context managers."""

import functools


def timed(func):
    """Decorator that stores the wrapped call's return value unchanged.

    Must use functools.wraps so the wrapped function keeps its __name__.
    (Timing itself isn't asserted in tests — this drills decorator plumbing.)
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def retry(times: int):
    """Decorator factory: retry the wrapped function up to `times` attempts,
    catching Exception, before letting the last exception propagate.

    Example:
        @retry(3)
        def flaky(): ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
            raise last_exc

        return wrapper

    return decorator


class suppressing:
    """Context manager that suppresses the given exception types.

    Example:
        with suppressing(KeyError):
            {}["missing"]
    """

    def __init__(self, *exceptions):
        self.exceptions = exceptions

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type is not None and issubclass(exc_type, self.exceptions)
