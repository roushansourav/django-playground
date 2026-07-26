"""Stage 0 exercise: comprehensions and generators."""


def dedupe_preserve_order(items: list) -> list:
    """Return items with duplicates removed, keeping first-seen order.

    Example: dedupe_preserve_order([1, 2, 1, 3, 2]) == [1, 2, 3]
    """
    raise NotImplementedError


def flatten_one_level(nested: list) -> list:
    """Flatten a list of lists by exactly one level.

    Example: flatten_one_level([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]
    """
    raise NotImplementedError


def evens_squared(nums: list) -> list:
    """Return the squares of the even numbers in nums, order preserved.

    Example: evens_squared([1, 2, 3, 4, 5]) == [4, 16]
    """
    raise NotImplementedError


def fibonacci(n: int):
    """Yield the first n Fibonacci numbers, starting 0, 1, 1, 2, 3, ...

    Must be a generator (use `yield`), not a function returning a list.
    """
    raise NotImplementedError
