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
