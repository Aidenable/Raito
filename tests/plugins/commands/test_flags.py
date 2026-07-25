"""Tests for raito.plugins.commands.flags (description / hidden / params)."""

from __future__ import annotations

from aiogram.dispatcher.flags import extract_flags_from_object

from raito.plugins.commands.flags import description, hidden, params


def test_description_sets_flag():
    @description("Ban a user")
    def handler(): ...

    flags = extract_flags_from_object(handler)
    assert flags["raito__description"] == "Ban a user"


def test_hidden_sets_flag():
    @hidden
    def handler(): ...

    flags = extract_flags_from_object(handler)
    assert flags["raito__hidden"] is True


def test_params_sets_flag():
    @params(user_id=int, reason=str)
    def handler(): ...

    flags = extract_flags_from_object(handler)
    assert flags["raito__params"] == {"user_id": int, "reason": str}


def test_params_empty():
    @params()
    def handler(): ...

    flags = extract_flags_from_object(handler)
    assert flags["raito__params"] == {}


def test_flags_combine_on_single_handler():
    @description("Warn user")
    @hidden
    @params(user_id=int)
    def handler(): ...

    flags = extract_flags_from_object(handler)
    assert flags["raito__description"] == "Warn user"
    assert flags["raito__hidden"] is True
    assert flags["raito__params"] == {"user_id": int}


def test_flags_do_not_leak_between_handlers():
    @description("only here")
    def a(): ...

    def b(): ...

    assert extract_flags_from_object(a)["raito__description"] == "only here"
    assert extract_flags_from_object(b) == {}
