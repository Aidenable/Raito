"""Tests for :class:`BasePaginator` navigation, math and validation."""

from __future__ import annotations

import pytest
from aiogram.types import InlineKeyboardMarkup

from raito.plugins.pagination import InlinePaginator
from raito.plugins.pagination.paginators.base import BasePaginator


def _set_loop(raito, value: bool) -> None:
    raito.configuration.pagination_style.loop_navigation = value


# --------------------------------------------------------------------------- #
# get_previous_page
# --------------------------------------------------------------------------- #


def test_previous_page_in_middle(make_paginator):
    paginator = make_paginator(current_page=3, total_pages=5)
    assert paginator.get_previous_page() == 2


@pytest.mark.parametrize("loop", [True, False])
def test_previous_page_in_middle_ignores_loop(make_paginator, raito, loop):
    _set_loop(raito, loop)
    paginator = make_paginator(current_page=4, total_pages=10)
    assert paginator.get_previous_page() == 3


def test_previous_page_first_with_loop_wraps_to_last(make_paginator, raito):
    _set_loop(raito, True)
    paginator = make_paginator(current_page=1, total_pages=5)
    assert paginator.get_previous_page() == 5


def test_previous_page_first_without_loop_stays(make_paginator, raito):
    _set_loop(raito, False)
    paginator = make_paginator(current_page=1, total_pages=5)
    assert paginator.get_previous_page() == 1


def test_previous_page_first_with_loop_but_no_total_stays(make_paginator, raito):
    _set_loop(raito, True)
    paginator = make_paginator(current_page=1, total_pages=None)
    # Cannot wrap without knowing the last page.
    assert paginator.get_previous_page() == 1


# --------------------------------------------------------------------------- #
# get_next_page
# --------------------------------------------------------------------------- #


def test_next_page_in_middle(make_paginator):
    paginator = make_paginator(current_page=2, total_pages=5)
    assert paginator.get_next_page() == 3


def test_next_page_last_with_loop_wraps_to_first(make_paginator, raito):
    _set_loop(raito, True)
    paginator = make_paginator(current_page=5, total_pages=5)
    assert paginator.get_next_page() == 1


def test_next_page_last_without_loop_stays(make_paginator, raito):
    _set_loop(raito, False)
    paginator = make_paginator(current_page=5, total_pages=5)
    assert paginator.get_next_page() == 5


@pytest.mark.parametrize("loop", [True, False])
def test_next_page_unlimited_when_total_is_none(make_paginator, raito, loop):
    _set_loop(raito, loop)
    paginator = make_paginator(current_page=7, total_pages=None)
    # No total pages means forward navigation is unbounded regardless of loop.
    assert paginator.get_next_page() == 8


# --------------------------------------------------------------------------- #
# calc_total_pages
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("total_items", "limit", "expected"),
    [
        (0, 20, 1),  # empty -> at least one page
        (1, 20, 1),
        (20, 20, 1),
        (21, 20, 2),
        (10, 3, 4),  # ceil(10 / 3)
        (9, 3, 3),
        (10, 5, 2),
        (100, 10, 10),
    ],
)
def test_calc_total_pages(total_items, limit, expected):
    assert BasePaginator.calc_total_pages(total_items, limit) == expected


@pytest.mark.parametrize("limit", [0, -1, -20])
def test_calc_total_pages_invalid_limit(limit):
    with pytest.raises(ValueError):
        BasePaginator.calc_total_pages(10, limit)


# --------------------------------------------------------------------------- #
# build_navigation
# --------------------------------------------------------------------------- #


def test_build_navigation_returns_markup(make_paginator):
    paginator = make_paginator(current_page=2, total_pages=5)
    markup = paginator.build_navigation()
    assert isinstance(markup, InlineKeyboardMarkup)
    # Flatten and ensure we actually built some buttons.
    buttons = [button for row in markup.inline_keyboard for button in row]
    assert buttons


def test_build_navigation_without_counter(make_paginator, raito):
    raito.configuration.pagination_style.show_counter = False
    paginator = make_paginator(current_page=2, total_pages=5)
    markup = paginator.build_navigation()
    buttons = [button for row in markup.inline_keyboard for button in row]
    # Only previous / next controls remain when the counter is hidden.
    assert len(buttons) == 2


# --------------------------------------------------------------------------- #
# _validate_parameters
# --------------------------------------------------------------------------- #


def test_valid_parameters_construct(make_paginator):
    paginator = make_paginator(name="p", current_page=1, total_pages=3, limit=20)
    assert paginator.current_page == 1
    assert paginator.total_pages == 3
    assert paginator.limit == 20


def test_empty_name_raises(make_paginator):
    with pytest.raises(ValueError):
        make_paginator(name="")


def test_too_long_name_raises(make_paginator):
    with pytest.raises(ValueError):
        make_paginator(name="x" * 33)


@pytest.mark.parametrize("current_page", [0, -1])
def test_current_page_below_one_raises(make_paginator, current_page):
    with pytest.raises(ValueError):
        make_paginator(current_page=current_page)


@pytest.mark.parametrize("limit", [0, -5])
def test_limit_below_one_raises(make_paginator, limit):
    with pytest.raises(ValueError):
        make_paginator(limit=limit)


def test_total_pages_below_current_raises(make_paginator):
    with pytest.raises(ValueError):
        make_paginator(current_page=5, total_pages=2)


def test_inline_limit_above_ninety_raises(make_paginator):
    # InlinePaginator narrows the base limit ceiling to 90.
    with pytest.raises(ValueError):
        make_paginator(paginator_cls=InlinePaginator, limit=91)
