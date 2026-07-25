"""Tests for :class:`raito.plugins.throttling.middleware.ThrottlingMiddleware`."""

from __future__ import annotations

import pytest
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import Update

from raito.plugins.throttling.flag import limiter
from raito.plugins.throttling.middleware import ThrottlingMiddleware


@pytest.fixture
def middleware() -> ThrottlingMiddleware:
    return ThrottlingMiddleware(rate_limit=100, mode="chat")


def make_handler():
    calls: list[int] = []

    async def handler(event, data):
        calls.append(1)
        return "handled"

    return handler, calls


# --------------------------------------------------------------------------- #
# _get_key
# --------------------------------------------------------------------------- #


def test_get_key_message_modes(middleware: ThrottlingMiddleware, make_message, bot) -> None:
    # chat_id / user_id default to 12345 in the factory; bind a bot for bot mode.
    message = make_message().as_(bot)

    assert middleware._get_key(message, "user") == message.from_user.id
    assert middleware._get_key(message, "chat") == message.chat.id
    assert middleware._get_key(message, "bot") == bot.id == 42


def test_get_key_message_without_bot_is_none(
    middleware: ThrottlingMiddleware, make_message
) -> None:
    # No bot bound -> guard returns None.
    assert middleware._get_key(make_message(), "chat") is None


def test_get_key_callback_modes(
    middleware: ThrottlingMiddleware, make_callback_query, make_message, make_chat, bot
) -> None:
    inner = make_message(chat=make_chat(chat_id=777)).as_(bot)
    callback = make_callback_query(message=inner).as_(bot)

    assert middleware._get_key(callback, "user") == callback.from_user.id
    assert middleware._get_key(callback, "chat") == 777
    assert middleware._get_key(callback, "bot") == 42


def test_get_key_unknown_event_is_none(middleware: ThrottlingMiddleware) -> None:
    assert middleware._get_key(Update(update_id=1), "chat") is None


# --------------------------------------------------------------------------- #
# __call__
# --------------------------------------------------------------------------- #


async def test_missing_handler_object_passes_through(
    middleware: ThrottlingMiddleware, make_message, bot
) -> None:
    handler, calls = make_handler()
    event = make_message().as_(bot)

    result = await middleware(handler, event, {"event_update": Update(update_id=1)})

    assert result == "handled"
    assert len(calls) == 1


async def test_first_call_passes_second_is_throttled(
    middleware: ThrottlingMiddleware, make_message, bot
) -> None:
    handler, calls = make_handler()
    event = make_message().as_(bot)
    data = {"handler": HandlerObject(callback=handler), "event_update": Update(update_id=1)}

    first = await middleware(handler, event, data)
    second = await middleware(handler, event, data)

    assert first == "handled"
    assert second is None
    assert len(calls) == 1


async def test_update_id_zero_skips_throttling(
    middleware: ThrottlingMiddleware, make_message, bot
) -> None:
    handler, calls = make_handler()
    event = make_message().as_(bot)
    data = {"handler": HandlerObject(callback=handler), "event_update": Update(update_id=0)}

    first = await middleware(handler, event, data)
    second = await middleware(handler, event, data)

    # update_id == 0 bypasses throttling entirely, so both calls run.
    assert first == "handled"
    assert second == "handled"
    assert len(calls) == 2


async def test_no_key_passes_through(middleware: ThrottlingMiddleware, make_message) -> None:
    handler, calls = make_handler()
    # No bot bound -> _get_key returns None -> handler always runs.
    event = make_message()
    data = {"handler": HandlerObject(callback=handler), "event_update": Update(update_id=1)}

    first = await middleware(handler, event, data)
    second = await middleware(handler, event, data)

    assert first == "handled"
    assert second == "handled"
    assert len(calls) == 2


async def test_local_limiter_flag_throttles_independently(make_message, bot) -> None:
    # Global window is tiny, but the per-handler limiter flag governs instead.
    middleware = ThrottlingMiddleware(rate_limit=0.0, mode="chat")

    calls: list[int] = []

    @limiter(100, mode="chat")
    async def handler(event, data):
        calls.append(1)
        return "handled"

    event = make_message().as_(bot)
    data = {"handler": HandlerObject(callback=handler), "event_update": Update(update_id=1)}

    first = await middleware(handler, event, data)
    second = await middleware(handler, event, data)

    assert first == "handled"
    assert second is None
    assert len(calls) == 1
