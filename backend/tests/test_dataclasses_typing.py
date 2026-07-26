"""Tests for backend/stage0_python_idioms/dataclasses_typing.py."""
import dataclasses

import pytest

from stage0_python_idioms.dataclasses_typing import Point, merge_records


def test_point_is_frozen():
    p = Point(1.0, 2.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.x = 5.0


def test_point_distance_to():
    a = Point(0.0, 0.0)
    b = Point(3.0, 4.0)
    assert a.distance_to(b) == 5.0


def test_merge_records_overrides_and_does_not_mutate():
    a = {"x": 1}
    b = {"x": 2, "y": 3}
    result = merge_records(a, b)
    assert result == {"x": 2, "y": 3}
    assert a == {"x": 1}
    assert b == {"x": 2, "y": 3}
