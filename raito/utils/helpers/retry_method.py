import asyncio
from collections.abc import Awaitable
from typing import TypeVar

from aiogram.exceptions import TelegramRetryAfter

T = TypeVar("T")


async def retry_method(
    func: Awaitable[T],
    max_attempts: int = 5,
    additional_delay: float = 0.1,
    *,
    _current_attempt: int = 1,
) -> T:
    """Retry a coroutine function if Telegram responds with RetryAfter.

    :param func: A coroutine function with no arguments.
    :param max_attempts: Maximum number of retry attempts.
    :param additional_delay: Extra seconds added to retry delay.
    :return: Result of the coroutine.
    :raises Exception: If all attempts fail or a non-RetryAfter exception is raised.
    """
    try:
        return await func
    except TelegramRetryAfter as exc:
        if _current_attempt >= max_attempts:
            raise

        await asyncio.sleep(exc.retry_after + additional_delay)
        return await retry_method(
            func,
            max_attempts,
            additional_delay,
            _current_attempt=_current_attempt + 1,
        )
