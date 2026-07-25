"""Tests for :class:`PaginationCallbackData` pack/unpack behaviour."""

from __future__ import annotations

import pytest

from raito.plugins.pagination.data import PaginationCallbackData


def test_prefix():
    assert PaginationCallbackData.__prefix__ == "rt_p"


def test_pack_unpack_roundtrip():
    data = PaginationCallbackData(
        mode=0,
        name="users",
        current_page=2,
        total_pages=5,
        limit=20,
    )
    restored = PaginationCallbackData.unpack(data.pack())

    assert restored == data
    assert restored.mode == 0
    assert restored.name == "users"
    assert restored.current_page == 2
    assert restored.total_pages == 5
    assert restored.limit == 20


def test_pack_unpack_roundtrip_with_none_total_pages():
    data = PaginationCallbackData(
        mode=4,
        name="p",
        current_page=1,
        total_pages=None,
        limit=10,
    )
    restored = PaginationCallbackData.unpack(data.pack())

    assert restored == data
    assert restored.total_pages is None


@pytest.mark.parametrize(
    ("mode", "name", "current_page", "total_pages", "limit"),
    [
        (0, "a", 1, 1, 1),
        (1, "text", 3, 10, 25),
        (2, "photo", 7, 7, 5),
        (3, "list_name", 1, None, 90),
        (4, "rich", 42, 100, 50),
    ],
)
def test_pack_unpack_preserves_all_fields(mode, name, current_page, total_pages, limit):
    data = PaginationCallbackData(
        mode=mode,
        name=name,
        current_page=current_page,
        total_pages=total_pages,
        limit=limit,
    )
    restored = PaginationCallbackData.unpack(data.pack())

    assert restored.mode == mode
    assert restored.name == name
    assert restored.current_page == current_page
    assert restored.total_pages == total_pages
    assert restored.limit == limit


def test_pack_starts_with_prefix():
    data = PaginationCallbackData(
        mode=1,
        name="p",
        current_page=1,
        total_pages=2,
        limit=20,
    )
    assert data.pack().startswith("rt_p:")
