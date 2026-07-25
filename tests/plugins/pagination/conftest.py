"""Fixtures shared by the pagination plugin tests."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from raito.plugins.pagination import InlinePaginator
from raito.plugins.pagination.paginators.base import BasePaginator


@pytest.fixture
def make_paginator(raito, bot, make_user) -> Callable[..., BasePaginator]:
    """Build a concrete paginator wired to the test fixtures.

    Uses :class:`InlinePaginator` because :class:`BasePaginator` is abstract
    (its ``mode`` property is not implemented).
    """

    def _make(
        *,
        name: str = "p",
        chat_id: int = 1,
        current_page: int = 1,
        total_pages: int | None = None,
        limit: int = 20,
        paginator_cls: type[BasePaginator] = InlinePaginator,
        **kwargs,
    ) -> BasePaginator:
        return paginator_cls(
            raito=raito,
            name=name,
            chat_id=chat_id,
            bot=bot,
            from_user=make_user(),
            current_page=current_page,
            total_pages=total_pages,
            limit=limit,
            **kwargs,
        )

    return _make
