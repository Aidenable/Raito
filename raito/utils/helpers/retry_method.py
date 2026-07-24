from __future__ import annotations

import asyncio
import inspect
import warnings
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from aiogram.exceptions import (
    TelegramNetworkError,
    TelegramRetryAfter,
    TelegramServerError,
)

P = ParamSpec("P")
T = TypeVar("T")

MAX_ATTEMPTS: int = 5
ADDITIONAL_DELAY: float = 0.1
MAX_DELAY: float = 30.0


async def retry_method(
    func: Callable[P, Awaitable[T]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    """Call an async function and retry it on Telegram errors.

    Pass the coroutine function together with its arguments.

    Example:

    .. code-block:: python

        await rt.retry(bot.send_message, chat_id, "text")
        await rt.retry(message.answer, "text")

    Retries on ``TelegramRetryAfter`` (honouring the server-provided
    ``retry_after``) and on network/server errors (``TelegramNetworkError``,
    ``TelegramServerError``) using exponential delay. Any other exception is
    raised immediately.

    :param func: A coroutine function to call on each attempt.
    :param args: Positional arguments forwarded to ``func``.
    :param kwargs: Keyword arguments forwarded to ``func``.
    :return: Result of the func.
    :raises Exception: If all attempts fail or a non-RetryAfter exception is raised.

    .. deprecated:: 1.6.0
       Passing an already-created coroutine (``rt.retry(bot.send_message(...))``)
       is deprecated and will stop working in 1.8.0. It is awaited only once and
       cannot be retried. Pass the function and its arguments instead:
       ``rt.retry(bot.send_message, chat_id, text)``.
    """
    if inspect.isawaitable(func):
        warnings.warn(
            "Passing an already-created coroutine to rt.retry is deprecated "
            "since 1.6.0 and will stop working in 1.8.0: a coroutine can only be "
            "awaited once, so it cannot be retried. Call it as "
            "rt.retry(func, *args, **kwargs). "
            "e.g. rt.retry(bot.send_message, chat_id, text) instead of "
            "rt.retry(bot.send_message(chat_id, text)).",
            DeprecationWarning,
            stacklevel=2,
        )
        return await func

    attempt: int = 0
    while True:
        attempt += 1

        try:
            return await func(*args, **kwargs)
        except TelegramRetryAfter as exc:
            if attempt >= MAX_ATTEMPTS:
                raise
            await asyncio.sleep(exc.retry_after + ADDITIONAL_DELAY)
        except (TelegramNetworkError, TelegramServerError):
            if attempt >= MAX_ATTEMPTS:
                raise
            await asyncio.sleep(min(ADDITIONAL_DELAY * 2 ** (attempt - 1), MAX_DELAY))
