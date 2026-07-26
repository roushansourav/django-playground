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
