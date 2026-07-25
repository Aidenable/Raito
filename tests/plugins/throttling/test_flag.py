"""Tests for :func:`raito.plugins.throttling.flag.limiter`."""

from __future__ import annotations

from aiogram.dispatcher.flags import extract_flags_from_object

from raito.plugins.throttling.flag import limiter


def test_limiter_sets_flag_with_defaults() -> None:
    @limiter(5)
    async def handler(message):
        return None

    flags = extract_flags_from_object(handler)
    assert flags["raito__limiter"] == {"rate_limit": 5, "mode": "user"}


def test_limiter_respects_custom_mode() -> None:
    @limiter(2.5, mode="chat")
    async def handler(message):
        return None

    flags = extract_flags_from_object(handler)
    assert flags["raito__limiter"] == {"rate_limit": 2.5, "mode": "chat"}
