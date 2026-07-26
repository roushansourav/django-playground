"""Stage 0 exercise: comprehensions and generators."""


def dedupe_preserve_order(items: list) -> list:
    """Return items with duplicates removed, keeping first-seen order.

    Example: dedupe_preserve_order([1, 2, 1, 3, 2]) == [1, 2, 3]
    """
    return list(dict.fromkeys(items))


def flatten_one_level(nested: list) -> list:
    """Flatten a list of lists by exactly one level.

    Example: flatten_one_level([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]
    """
    return [item for sublist in nested for item in sublist]


def evens_squared(nums: list) -> list:
    """Return the squares of the even numbers in nums, order preserved.

    Example: evens_squared([1, 2, 3, 4, 5]) == [4, 16]
    """
    return [n * n for n in nums if n % 2 == 0]


def fibonacci(n: int):
    """Yield the first n Fibonacci numbers, starting 0, 1, 1, 2, 3, ...

    Must be a generator (use `yield`), not a function returning a list.
    """
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
