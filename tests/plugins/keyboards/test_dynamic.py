"""Tests for raito.plugins.keyboards.dynamic (``@rt.keyboard.dynamic``)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from raito import rt


def test_dynamic_inline_builds_markup():
    @rt.keyboard.dynamic(inline=True)
    def markup(builder):
        builder.button(text="A", callback_data="a")
        builder.button(text="B", callback_data="b")

    result = markup()
    assert isinstance(result, InlineKeyboardMarkup)
    texts = [b.text for row in result.inline_keyboard for b in row]
    assert texts == ["A", "B"]


def test_dynamic_builder_is_first_argument():
    seen = {}

    @rt.keyboard.dynamic(inline=True)
    def markup(builder):
        seen["is_inline_builder"] = isinstance(builder, InlineKeyboardBuilder)
        builder.button(text="X", callback_data="x")

    markup()
    assert seen["is_inline_builder"] is True


def test_dynamic_reply_builder_type():
    captured = {}

    @rt.keyboard.dynamic(inline=False)
    def markup(builder):
        captured["is_reply_builder"] = isinstance(builder, ReplyKeyboardBuilder)
        builder.button(text="One")
        builder.button(text="Two")

    result = markup()
    assert isinstance(result, ReplyKeyboardMarkup)
    assert captured["is_reply_builder"] is True
    texts = [b.text for row in result.keyboard for b in row]
    assert texts == ["One", "Two"]
    assert result.resize_keyboard is True


def test_dynamic_extra_params_are_forwarded():
    @rt.keyboard.dynamic(inline=True)
    def markup(builder, name=None):
        if name is not None:
            builder.button(text=f"Hi {name}", callback_data="hi")
        builder.button(text="Back", callback_data="back")

    with_name = markup(name="Bob")
    texts = [b.text for row in with_name.inline_keyboard for b in row]
    assert "Hi Bob" in texts
    assert "Back" in texts

    without_name = markup()
    texts_without = [b.text for row in without_name.inline_keyboard for b in row]
    assert texts_without == ["Back"]


def test_dynamic_positional_param_forwarded():
    @rt.keyboard.dynamic(inline=True)
    def markup(builder, count):
        for i in range(count):
            builder.button(text=str(i), callback_data=str(i))

    result = markup(3)
    texts = [b.text for row in result.inline_keyboard for b in row]
    assert texts == ["0", "1", "2"]


def test_dynamic_adjust_sizes():
    @rt.keyboard.dynamic(2, inline=True)
    def markup(builder):
        for i in range(4):
            builder.button(text=str(i), callback_data=str(i))

    result = markup()
    # adjust(2, repeat=True) -> two rows of two buttons each
    assert [len(row) for row in result.inline_keyboard] == [2, 2]
