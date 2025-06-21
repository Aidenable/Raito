from collections.abc import Awaitable, Callable
from typing import Any, Literal, TypeVar

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from cachetools import TTLCache

R = TypeVar("R")

__all__ = ("ThrottlingMiddleware",)


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for throttling message and callback query processing.

    Prevents spam by limiting the rate at which users can send messages
    or trigger callback queries based on different throttling modes.
    """

    MODE = Literal["chat", "user", "bot"]

    def __init__(
        self,
        rate_limit: float = 0.5,
        mode: MODE = "chat",
        max_size: int = 10_000,
    ) -> None:
        """Initialize ThrottlingMiddleware.

        :param rate_limit: Time in seconds between allowed requests, defaults to 0.5
        :type rate_limit: float, optional
        :param mode: Throttling mode - 'chat', 'user', or 'bot', defaults to 'chat'
        :type mode: MODE, optional
        :param max_size: Maximum cache size for throttling records, defaults to 10_000
        :type max_size: int, optional
        """
        self.rate_limit = rate_limit
        self.mode = mode
        self.max_size = max_size

        self.cache: TTLCache[int, bool] = TTLCache(maxsize=self.max_size, ttl=self.rate_limit)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        """Process incoming events with throttling logic.

        Checks if the event should be throttled based on the configured mode
        and rate limit. If throttled, returns None to skip processing.

        :param handler: Next handler in the middleware chain
        :type handler: Callable
        :param event: Telegram event (Message or CallbackQuery)
        :type event: TelegramObject
        :param data: Additional data passed through the middleware chain
        :type data: dict[str, Any]
        :return: Handler result if not throttled, None if throttled
        :rtype: Any | None
        :raises ValueError: If an invalid throttling mode is configured
        """
        chat_id: int

        if isinstance(event, Message) and event.from_user and event.bot:
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery) and event.message and event.from_user and event.bot:
            chat_id = event.message.chat.id
        else:
            return await handler(event, data)

        match self.mode:
            case "chat":
                key = chat_id
            case "user":
                key = event.from_user.id
            case "bot":
                key = event.bot.id
            case _:
                msg = f"Invalid mode: {self.mode}"
                raise ValueError(msg)

        if key in self.cache:
            return None

        self.cache[key] = False
        return await handler(event, data)
