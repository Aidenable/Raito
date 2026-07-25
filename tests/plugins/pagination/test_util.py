"""Tests for :func:`get_paginator`."""

from __future__ import annotations

import pytest

from raito.plugins.pagination import (
    InlinePaginator,
    ListPaginator,
    PhotoPaginator,
    RichPaginator,
    TextPaginator,
)
from raito.plugins.pagination.enums import PaginationMode
from raito.plugins.pagination.util import get_paginator


@pytest.mark.parametrize(
    ("mode", "expected_cls"),
    [
        (PaginationMode.INLINE, InlinePaginator),
        (PaginationMode.TEXT, TextPaginator),
        (PaginationMode.PHOTO, PhotoPaginator),
        (PaginationMode.LIST, ListPaginator),
        (PaginationMode.RICH, RichPaginator),
    ],
)
def test_get_paginator_returns_expected_class(mode, expected_cls):
    assert get_paginator(mode) is expected_cls


def test_get_paginator_invalid_mode_raises():
    with pytest.raises(ValueError):
        get_paginator(999)  # type: ignore[arg-type]
