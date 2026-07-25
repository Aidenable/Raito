"""Tests for :mod:`raito.plugins.conversations.waiter`."""

from __future__ import annotations

import asyncio

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from raito.plugins.conversations.waiter import Waiter, wait_for


def test_waiter_is_a_dataclass_container(make_message) -> None:
    message = make_message(text="hello")

    async def retry() -> Waiter:  # pragma: no cover - never awaited here
        raise AssertionError

    waiter = Waiter(text="hello", number=None, message=message, retry=retry)
    assert waiter.text == "hello"
    assert waiter.number is None
    assert waiter.message is message
    assert waiter.retry is retry


async def test_wait_for_parses_digit_text(raito, storage, make_message) -> None:
    key = StorageKey(bot_id=42, chat_id=1, user_id=1)
    context = FSMContext(storage=storage, key=key)

    task = asyncio.create_task(wait_for(raito, context))
    await asyncio.sleep(0)

    # wait_for parks the FSM in the conversation state while listening.
    assert await context.get_state() == raito.registry.STATE

    message = make_message(text="42")
    raito.registry.resolve(key, message)

    waiter = await asyncio.wait_for(task, timeout=1)
    assert waiter.text == "42"
    assert waiter.number == 42
    assert waiter.message is message
    assert callable(waiter.retry)


async def test_wait_for_non_digit_text_has_no_number(raito, storage, make_message) -> None:
    key = StorageKey(bot_id=42, chat_id=1, user_id=1)
    context = FSMContext(storage=storage, key=key)

    task = asyncio.create_task(wait_for(raito, context))
    await asyncio.sleep(0)

    message = make_message(text="hello world")
    raito.registry.resolve(key, message)

    waiter = await asyncio.wait_for(task, timeout=1)
    assert waiter.text == "hello world"
    assert waiter.number is None
