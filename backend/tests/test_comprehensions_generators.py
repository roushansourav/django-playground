"""Tests for backend/stage0_python_idioms/comprehensions_generators.py."""
import inspect

from stage0_python_idioms.comprehensions_generators import (
    dedupe_preserve_order,
    evens_squared,
    fibonacci,
    flatten_one_level,
)


def test_dedupe_preserve_order():
    assert dedupe_preserve_order([1, 2, 1, 3, 2]) == [1, 2, 3]


def test_dedupe_preserve_order_empty():
    assert dedupe_preserve_order([]) == []


def test_flatten_one_level():
    assert flatten_one_level([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]


def test_evens_squared():
    assert evens_squared([1, 2, 3, 4, 5]) == [4, 16]


def test_fibonacci_is_generator():
    assert inspect.isgeneratorfunction(fibonacci)


def test_fibonacci_first_seven():
    assert list(fibonacci(7)) == [0, 1, 1, 2, 3, 5, 8]
