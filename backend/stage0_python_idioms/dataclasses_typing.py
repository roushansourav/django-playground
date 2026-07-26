"""Stage 0 exercise: dataclasses and typing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """An immutable 2D point.

    Fields: x: float, y: float.
    """

    x: float = 0.0
    y: float = 0.0

    def distance_to(self, other: "Point") -> float:
        """Euclidean distance to another Point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


def merge_records(a: dict, b: dict) -> dict:
    """Merge two dicts; keys in b override keys in a. Neither input is mutated.

    Example: merge_records({"x": 1}, {"x": 2, "y": 3}) == {"x": 2, "y": 3}
    """
    return {**a, **b}
