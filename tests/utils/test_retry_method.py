import asyncio

import pytest
from aiogram.exceptions import (
    TelegramNetworkError,
    TelegramRetryAfter,
    TelegramServerError,
)

from raito.utils.helpers import retry_method as retry_module
from raito.utils.helpers.retry_method import retry_method


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Avoid real delays: replace asyncio.sleep with an async no-op."""

    async def _fake_sleep(_seconds):
        return None

    monkeypatch.setattr(retry_module.asyncio, "sleep", _fake_sleep)


async def test_success_first_attempt():
    calls = 0

    async def func(a, b):
        nonlocal calls
        calls += 1
        return a + b

    result = await retry_method(func, 2, 3)
    assert result == 5
    assert calls == 1


async def test_retries_on_retry_after_then_succeeds():
    calls = 0

    async def func():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TelegramRetryAfter(method="m", message="x", retry_after=0)
        return "done"

    result = await retry_method(func)
    assert result == "done"
    assert calls == 2


async def test_retries_on_network_error_then_succeeds():
    calls = 0

    async def func():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TelegramNetworkError(method="m", message="boom")
        return "ok"

    result = await retry_method(func)
    assert result == "ok"
    assert calls == 3


async def test_retries_on_server_error_then_succeeds():
    calls = 0

    async def func():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TelegramServerError(method="m", message="500")
        return "recovered"

    result = await retry_method(func)
    assert result == "recovered"
    assert calls == 2


async def test_exhausts_attempts_and_reraises_retry_after():
    calls = 0

    async def func():
        nonlocal calls
        calls += 1
        raise TelegramRetryAfter(method="m", message="x", retry_after=0)

    with pytest.raises(TelegramRetryAfter):
        await retry_method(func)
    assert calls == retry_module.MAX_ATTEMPTS


async def test_exhausts_attempts_and_reraises_network_error():
    calls = 0

    async def func():
        nonlocal calls
        calls += 1
        raise TelegramNetworkError(method="m", message="boom")

    with pytest.raises(TelegramNetworkError):
        await retry_method(func)
    assert calls == retry_module.MAX_ATTEMPTS


async def test_other_exceptions_are_raised_immediately():
    calls = 0

    async def func():
        nonlocal calls
        calls += 1
        raise ValueError("nope")

    with pytest.raises(ValueError):
        await retry_method(func)
    assert calls == 1


async def test_passing_created_coroutine_is_deprecated_but_awaited():
    async def coro():
        return "legacy"

    with pytest.warns(DeprecationWarning):
        result = await retry_method(coro())
    assert result == "legacy"
