from collections.abc import Awaitable, Callable
from typing import Any, Literal

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):  # type: ignore[misc]
    MODE = Literal["chat", "user", "bot"]

    def __init__(
        self, rate_limit: float = 0.5, mode: MODE = "chat", max_size: int = 10_000
    ) -> None:
        self.rate_limit = rate_limit
        self.mode = mode
        self.max_size = max_size

        self.cache: TTLCache[int, bool] = TTLCache(maxsize=self.max_size, ttl=self.rate_limit)

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat_id: int

        if isinstance(event, types.Message) and event.from_user and event.bot:
            chat_id = event.chat.id
        elif (
            isinstance(event, types.CallbackQuery)
            and event.message
            and event.from_user
            and event.bot
        ):
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
                raise ValueError(f"Invalid mode: {self.mode}")

        if key in self.cache:
            return None

        self.cache[key] = False
        return await handler(event, data)
