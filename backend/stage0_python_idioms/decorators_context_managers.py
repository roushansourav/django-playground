"""Stage 0 exercise: decorators and context managers."""

import functools


def timed(func):
    """Decorator that stores the wrapped call's return value unchanged.

    Must use functools.wraps so the wrapped function keeps its __name__.
    (Timing itself isn't asserted in tests — this drills decorator plumbing.)
    """
    raise NotImplementedError


def retry(times: int):
    """Decorator factory: retry the wrapped function up to `times` attempts,
    catching Exception, before letting the last exception propagate.

    Example:
        @retry(3)
        def flaky(): ...
    """
    raise NotImplementedError


class suppressing:
    """Context manager that suppresses the given exception types.

    Example:
        with suppressing(KeyError):
            {}["missing"]
    """

    def __init__(self, *exceptions):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError
