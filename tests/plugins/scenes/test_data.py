"""Tests for :class:`raito.plugins.scenes.data.SceneData`."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from raito.plugins.scenes.data import SceneData


class Draft(SceneData):
    username: str = ""
    age: int = 0


def test_starts_from_defaults() -> None:
    draft = Draft()
    assert draft.username == ""
    assert draft.age == 0


def test_fields_are_mutable() -> None:
    draft = Draft()
    draft.username = "alice"
    draft.age = 30
    assert draft.username == "alice"
    assert draft.age == 30


def test_extra_field_forbidden() -> None:
    with pytest.raises(ValidationError):
        Draft(unknown="value")


def test_assignment_is_validated() -> None:
    draft = Draft()
    with pytest.raises(ValidationError):
        draft.age = "not-an-int"
