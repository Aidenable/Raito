"""Tests for :class:`PaginationMode`."""

from __future__ import annotations

from enum import IntEnum

import pytest

from raito.plugins.pagination.enums import PaginationMode


def test_is_int_enum():
    assert issubclass(PaginationMode, IntEnum)


@pytest.mark.parametrize(
    ("member", "value"),
    [
        (PaginationMode.INLINE, 0),
        (PaginationMode.TEXT, 1),
        (PaginationMode.PHOTO, 2),
        (PaginationMode.LIST, 3),
        (PaginationMode.RICH, 4),
    ],
)
def test_values(member, value):
    assert member.value == value
    assert member == value


def test_unique_values():
    values = [member.value for member in PaginationMode]
    assert len(values) == len(set(values))


def test_all_members_present():
    assert {member.name for member in PaginationMode} == {
        "INLINE",
        "TEXT",
        "PHOTO",
        "LIST",
        "RICH",
    }
