# Stage 0: Python Idioms Refresher — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap the `backend/` Python environment and scaffold four exercise modules
(comprehensions/generators, decorators/context managers, dataclasses/typing, OOP/mixin
patterns) with failing tests, ready for the learner to implement.

**Architecture:** Plain Python package under `backend/stage0_python_idioms/`, no Django
dependency yet (Django is introduced in Stage 1). Each concept gets one module of
`NotImplementedError` stubs and one pytest file exercising them. This plan produces the
*scaffolding* only — per the spec's exercise/solution workflow, the learner implements the
stubs interactively (concept explained → learner attempts), and a reference solution is
built afterward on a `solution/stage-0` branch. A task in this plan is "done" when its
tests fail for the *expected* reason (`NotImplementedError`), not when they pass.

**Tech Stack:** Python 3, pytest.

## Global Constraints

- Database/API/frontend: none — Stage 0 is pure Python, no Django yet (per spec).
- Location: `~/django-playground/backend/` (repo already initialized at `~/django-playground`).
- No placeholders beyond the intentional `NotImplementedError` stubs — every function has a
  real docstring and a real, concrete test asserting real expected values.

---

### Task 1: Bootstrap backend Python environment

**Files:**
- Create: `backend/.gitignore`
- Create: `backend/requirements-dev.txt`
- Create: `backend/pytest.ini`
- Create: `backend/stage0_python_idioms/__init__.py`
- Create: `backend/tests/__init__.py`

**Interfaces:**
- Produces: a `backend/` directory with a working venv at `backend/.venv`, `pytest`
  installed, and `pytest` runnable from `backend/` with zero collected tests (nothing
  exists yet).

- [ ] **Step 1: Create directories and virtualenv**

```bash
mkdir -p ~/django-playground/backend/stage0_python_idioms
mkdir -p ~/django-playground/backend/tests
cd ~/django-playground/backend
python3 -m venv .venv
```

- [ ] **Step 2: Install pytest and freeze requirements**

```bash
cd ~/django-playground/backend
.venv/bin/pip install pytest
.venv/bin/pip freeze > requirements-dev.txt
```

- [ ] **Step 3: Create `backend/.gitignore`**

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 4: Create `backend/pytest.ini`**

```ini
[pytest]
testpaths = tests
```

- [ ] **Step 5: Create empty package markers**

```bash
touch ~/django-playground/backend/stage0_python_idioms/__init__.py
touch ~/django-playground/backend/tests/__init__.py
```

- [ ] **Step 6: Verify pytest runs with zero tests**

Run: `cd ~/django-playground/backend && .venv/bin/pytest -v`
Expected: `no tests ran` (exit code 5) — confirms the environment works before any test
files exist.

- [ ] **Step 7: Commit**

```bash
cd ~/django-playground
git add backend/.gitignore backend/requirements-dev.txt backend/pytest.ini \
  backend/stage0_python_idioms/__init__.py backend/tests/__init__.py
git commit -m "Bootstrap backend Python environment for Stage 0"
```

---

### Task 2: Comprehensions & generators exercise

**Files:**
- Create: `backend/stage0_python_idioms/comprehensions_generators.py`
- Test: `backend/tests/test_comprehensions_generators.py`

**Interfaces:**
- Produces: `dedupe_preserve_order(items: list) -> list`,
  `flatten_one_level(nested: list[list]) -> list`,
  `evens_squared(nums: list[int]) -> list[int]`,
  `fibonacci(n: int) -> Generator[int, None, None]` — all raising `NotImplementedError`
  until the learner implements them.

- [ ] **Step 1: Write the stub module**

```python
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
```

- [ ] **Step 2: Write the failing tests**

```python
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
```

- [ ] **Step 3: Run tests, verify they fail with `NotImplementedError`**

Run: `cd ~/django-playground/backend && .venv/bin/pytest tests/test_comprehensions_generators.py -v`
Expected: all tests FAIL, each raising `NotImplementedError` (the `test_fibonacci_is_generator`
test passes immediately since the stub uses `yield`... — wait, `fibonacci` uses `raise
NotImplementedError` with no `yield`, so it is not a generator function yet; that test is
expected to FAIL too, and will only pass once the learner adds a `yield` statement).

- [ ] **Step 4: Commit**

```bash
cd ~/django-playground
git add backend/stage0_python_idioms/comprehensions_generators.py \
  backend/tests/test_comprehensions_generators.py
git commit -m "Add Stage 0 exercise: comprehensions and generators"
```

---

### Task 3: Decorators & context managers exercise

**Files:**
- Create: `backend/stage0_python_idioms/decorators_context_managers.py`
- Test: `backend/tests/test_decorators_context_managers.py`

**Interfaces:**
- Produces: `timed(func)` (decorator), `retry(times: int)` (decorator factory),
  `suppressing(*exceptions)` (context manager, class-based) — all raising
  `NotImplementedError` until implemented.

- [ ] **Step 1: Write the stub module**

```python
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
```

- [ ] **Step 2: Write the failing tests**

```python
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
```

- [ ] **Step 3: Run tests, verify they fail with `NotImplementedError`**

Run: `cd ~/django-playground/backend && .venv/bin/pytest tests/test_decorators_context_managers.py -v`
Expected: all tests FAIL with `NotImplementedError`.

- [ ] **Step 4: Commit**

```bash
cd ~/django-playground
git add backend/stage0_python_idioms/decorators_context_managers.py \
  backend/tests/test_decorators_context_managers.py
git commit -m "Add Stage 0 exercise: decorators and context managers"
```

---

### Task 4: Dataclasses & typing exercise

**Files:**
- Create: `backend/stage0_python_idioms/dataclasses_typing.py`
- Test: `backend/tests/test_dataclasses_typing.py`

**Interfaces:**
- Produces: `Point` (frozen dataclass with `x: float, y: float` and a `distance_to`
  method), `merge_records(a: dict, b: dict) -> dict` (typed dict-merge helper) — raising
  `NotImplementedError` until implemented.

- [ ] **Step 1: Write the stub module**

```python
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
        raise NotImplementedError


def merge_records(a: dict, b: dict) -> dict:
    """Merge two dicts; keys in b override keys in a. Neither input is mutated.

    Example: merge_records({"x": 1}, {"x": 2, "y": 3}) == {"x": 2, "y": 3}
    """
    raise NotImplementedError
```

- [ ] **Step 2: Write the failing tests**

```python
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
```

- [ ] **Step 3: Run tests, verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/pytest tests/test_dataclasses_typing.py -v`
Expected: `test_point_is_frozen` PASSES already (frozen=True is set in the stub); the other
two FAIL with `NotImplementedError`. This is expected — the stub only leaves the *logic*
unimplemented, not the dataclass configuration.

- [ ] **Step 4: Commit**

```bash
cd ~/django-playground
git add backend/stage0_python_idioms/dataclasses_typing.py \
  backend/tests/test_dataclasses_typing.py
git commit -m "Add Stage 0 exercise: dataclasses and typing"
```

---

### Task 5: OOP / mixin patterns exercise

**Files:**
- Create: `backend/stage0_python_idioms/oop_patterns.py`
- Test: `backend/tests/test_oop_patterns.py`

**Interfaces:**
- Produces: `TimestampedMixin`, `SerializableMixin`, and `Note` (combines both mixins) —
  drills the mixin composition pattern Django's class-based views use heavily.

- [ ] **Step 1: Write the stub module**

```python
"""Stage 0 exercise: OOP mixin patterns (as used by Django's class-based views)."""


class TimestampedMixin:
    """Adds a `created_at` attribute set at construction time via `_now()`.

    Subclasses must call `self._init_timestamp()` in their __init__.
    `_now()` returns a fixed value here so tests are deterministic — do not
    use real wall-clock time.
    """

    def _now(self) -> str:
        return "2026-01-01T00:00:00Z"

    def _init_timestamp(self) -> None:
        raise NotImplementedError


class SerializableMixin:
    """Adds a `to_dict()` method that serializes all attributes set on
    `self.__dict__` into a plain dict.
    """

    def to_dict(self) -> dict:
        raise NotImplementedError


class Note(TimestampedMixin, SerializableMixin):
    """A note with a title and body, timestamped and serializable."""

    def __init__(self, title: str, body: str):
        self.title = title
        self.body = body
        raise NotImplementedError  # call self._init_timestamp() here, then remove this line
```

- [ ] **Step 2: Write the failing tests**

```python
"""Tests for backend/stage0_python_idioms/oop_patterns.py."""
from stage0_python_idioms.oop_patterns import Note


def test_note_has_timestamp():
    note = Note("Title", "Body")
    assert note.created_at == "2026-01-01T00:00:00Z"


def test_note_to_dict_contains_all_fields():
    note = Note("Title", "Body")
    d = note.to_dict()
    assert d == {
        "title": "Title",
        "body": "Body",
        "created_at": "2026-01-01T00:00:00Z",
    }


def test_note_mro_is_note_then_timestamped_then_serializable():
    mro_names = [cls.__name__ for cls in Note.__mro__]
    assert mro_names[:3] == ["Note", "TimestampedMixin", "SerializableMixin"]
```

- [ ] **Step 3: Run tests, verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/pytest tests/test_oop_patterns.py -v`
Expected: `test_note_mro_is_note_then_timestamped_then_serializable` PASSES already (MRO is
fixed by the class declaration, not by the unimplemented logic); the other two FAIL,
raising `NotImplementedError` from `Note.__init__`.

- [ ] **Step 4: Commit**

```bash
cd ~/django-playground
git add backend/stage0_python_idioms/oop_patterns.py \
  backend/tests/test_oop_patterns.py
git commit -m "Add Stage 0 exercise: OOP mixin patterns"
```

---

## After this plan

This plan only scaffolds the exercises. Next, work through each module with the learner:
explain the concept, let them implement the stub, run pytest to confirm it passes, then
build a reference version on a `solution/stage-0` branch per the spec's workflow. Stage 1
(Django fundamentals + Blog CRUD) gets its own plan once Stage 0 is done.
