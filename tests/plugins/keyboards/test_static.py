"""Tests for raito.plugins.keyboards.static (``@rt.keyboard.static``)."""

from __future__ import annotations

import pytest
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from raito import rt


# --------------------------------------------------------------------------- #
# Inline keyboards
# --------------------------------------------------------------------------- #
def test_inline_single_button():
    @rt.keyboard.static()
    def markup():
        return [("Text", "cb")]

    result = markup()
    assert isinstance(result, InlineKeyboardMarkup)
    assert len(result.inline_keyboard) == 1
    row = result.inline_keyboard[0]
    assert len(row) == 1
    assert row[0].text == "Text"
    assert row[0].callback_data == "cb"
    assert row[0].url is None


def test_inline_row_of_two_buttons():
    @rt.keyboard.static()
    def markup():
        return [[("A", "a"), ("B", "b")]]

    result = markup()
    assert isinstance(result, InlineKeyboardMarkup)
    assert len(result.inline_keyboard) == 1
    row = result.inline_keyboard[0]
    assert [b.text for b in row] == ["A", "B"]
    assert [b.callback_data for b in row] == ["a", "b"]


def test_inline_multiple_rows():
    @rt.keyboard.static()
    def markup():
        return [
            ("Top", "top"),
            [("Left", "l"), ("Right", "r")],
        ]

    result = markup()
    assert len(result.inline_keyboard) == 2
    assert len(result.inline_keyboard[0]) == 1
    assert len(result.inline_keyboard[1]) == 2
    assert result.inline_keyboard[0][0].text == "Top"


@pytest.mark.parametrize(
    ("value", "expected_url"),
    [
        ("https://example.com", "https://example.com"),
        ("http://example.com", "http://example.com"),
        ("tg://resolve?domain=x", "tg://resolve?domain=x"),
        ("t.me/some_channel", "https://t.me/some_channel"),
    ],
)
def test_inline_url_detection(value, expected_url):
    @rt.keyboard.static()
    def markup():
        return [("Link", value)]

    button = markup().inline_keyboard[0][0]
    assert button.url == expected_url
    assert button.callback_data is None


def test_inline_plain_value_is_callback_data():
    @rt.keyboard.static()
    def markup():
        return [("Btn", "just_a_callback")]

    button = markup().inline_keyboard[0][0]
    assert button.url is None
    assert button.callback_data == "just_a_callback"


def test_inline_string_button_raises_value_error():
    @rt.keyboard.static()
    def markup():
        return ["not a tuple"]

    with pytest.raises(ValueError, match="tuple of"):
        markup()


def test_inline_single_element_tuple_raises_value_error():
    @rt.keyboard.static()
    def markup():
        return [("only",)]

    with pytest.raises(ValueError, match="tuple of"):
        markup()


def test_non_list_return_raises_type_error():
    @rt.keyboard.static()
    def markup():
        return ("a", "b")

    with pytest.raises(TypeError, match="must return a list"):
        markup()


# --------------------------------------------------------------------------- #
# Reply keyboards
# --------------------------------------------------------------------------- #
def test_reply_single_string_button():
    @rt.keyboard.static(inline=False)
    def markup():
        return ["Single"]

    result = markup()
    assert isinstance(result, ReplyKeyboardMarkup)
    assert len(result.keyboard) == 1
    assert result.keyboard[0][0].text == "Single"


def test_reply_list_of_strings_yields_two_buttons():
    """A top-level list of strings produces one single-button row per string.

    Important: ``["Yes", "No"]`` is the *layout* (a list of rows), so each
    string becomes its own row with a single button.
    """

    @rt.keyboard.static(inline=False)
    def markup():
        return ["Yes", "No"]

    result = markup()
    assert len(result.keyboard) == 2
    assert [row[0].text for row in result.keyboard] == ["Yes", "No"]
    assert all(len(row) == 1 for row in result.keyboard)


def test_reply_multi_button_row():
    """Three strings in one row bypass the single-button detection."""

    @rt.keyboard.static(inline=False)
    def markup():
        return [["A", "B", "C"]]

    result = markup()
    assert len(result.keyboard) == 1
    assert [b.text for b in result.keyboard[0]] == ["A", "B", "C"]


def test_reply_defaults_to_resize_keyboard():
    @rt.keyboard.static(inline=False)
    def markup():
        return ["Ok"]

    assert markup().resize_keyboard is True
