"""Tests for backend/stage0_python_idioms/decorators_context_managers.py."""
from stage0_python_idioms.decorators_context_managers import (
    retry,
    suppressing,
    timed,
)


def test_timed_preserves_name_and_return_value():
    @timed
    def add(a, b):
        return a + b

    assert add.__name__ == "add"
    assert add(2, 3) == 5


def test_retry_succeeds_after_failures():
    attempts = {"count": 0}

    @retry(3)
    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("not yet")
        return "ok"

    assert flaky() == "ok"
    assert attempts["count"] == 3


def test_retry_raises_after_exhausting_attempts():
    @retry(2)
    def always_fails():
        raise ValueError("nope")

    try:
        always_fails()
        assert False, "expected ValueError to propagate"
    except ValueError:
        pass


def test_suppressing_swallows_matching_exception():
    with suppressing(KeyError):
        {}["missing"]
    # if we get here, the exception was suppressed


def test_suppressing_lets_other_exceptions_propagate():
    try:
        with suppressing(KeyError):
            raise ValueError("different exception")
        assert False, "expected ValueError to propagate"
    except ValueError:
        pass
