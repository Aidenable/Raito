"""Tests for :class:`raito.plugins.conversations.registry.ConversationRegistry`."""

from __future__ import annotations

import asyncio

import pytest
from aiogram.fsm.storage.base import StorageKey

from raito.plugins.conversations.registry import ConversationRegistry


@pytest.fixture
def key() -> StorageKey:
    return StorageKey(bot_id=42, chat_id=1, user_id=1)


@pytest.fixture
def registry() -> ConversationRegistry:
    return ConversationRegistry()


async def test_listen_returns_pending_future(
    registry: ConversationRegistry, key: StorageKey
) -> None:
    future = registry.listen(key)
    assert isinstance(future, asyncio.Future)
    assert not future.done()


async def test_listen_registers_filters(registry: ConversationRegistry, key: StorageKey) -> None:
    def flt(message):  # pragma: no cover - identity filter, never called here
        return True

    registry.listen(key, flt)
    assert registry.get_filters(key) == (flt,)


async def test_get_filters_none_when_absent(
    registry: ConversationRegistry, key: StorageKey
) -> None:
    assert registry.get_filters(key) is None


async def test_relisten_cancels_previous_future(
    registry: ConversationRegistry, key: StorageKey
) -> None:
    first = registry.listen(key)
    second = registry.listen(key)

    assert first.cancelled() is True
    assert not second.done()
    # The newest future is the active one.
    assert second is not first


async def test_resolve_completes_and_removes(
    registry: ConversationRegistry, key: StorageKey, make_message
) -> None:
    future = registry.listen(key)
    message = make_message()

    registry.resolve(key, future_message := message)

    assert future.done()
    assert future.result() is future_message
    # The entry is popped after resolving.
    assert registry.get_filters(key) is None


async def test_resolve_missing_key_is_noop(
    registry: ConversationRegistry, key: StorageKey, make_message
) -> None:
    # Should not raise even though nothing is listening.
    registry.resolve(key, make_message())
    assert registry.get_filters(key) is None


async def test_cancel_cancels_future_and_removes(
    registry: ConversationRegistry, key: StorageKey
) -> None:
    future = registry.listen(key)

    registry.cancel(key)

    assert future.cancelled() is True
    assert registry.get_filters(key) is None


async def test_cancel_missing_key_is_noop(registry: ConversationRegistry, key: StorageKey) -> None:
    # Nothing registered — cancel is a no-op.
    registry.cancel(key)
    assert registry.get_filters(key) is None


async def test_awaiting_future_yields_resolved_message(
    registry: ConversationRegistry, key: StorageKey, make_message
) -> None:
    future = registry.listen(key)
    message = make_message(text="hello")

    async def responder() -> None:
        await asyncio.sleep(0)
        registry.resolve(key, message)

    asyncio.create_task(responder())
    received = await asyncio.wait_for(future, timeout=1)
    assert received is message
