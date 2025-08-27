from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message, Update
from cachetools import TTLCache
from typing_extensions import override

if TYPE_CHECKING:
    from aiogram.types import TelegramObject

R = TypeVar("R")

__all__ = (
    "THROTTLING_MODE",
    "ThrottlingMiddleware",
)

THROTTLING_MODE = Literal["user", "chat", "bot"]


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for global and per-handler throttling."""

    def __init__(
        self,
        rate_limit: float = 0.5,
        mode: THROTTLING_MODE = "chat",
        max_size: int = 10_000,
    ) -> None:
        """Initialize the middleware.

        :param rate_limit: Global throttling timeout (seconds)
        :param mode: Throttling scope — 'user', 'chat', or 'bot'
        :param max_size: Maximum number of keys stored in cache
        """
        self.rate_limit = rate_limit
        self.mode: THROTTLING_MODE = mode
        self.max_size = max_size

        self._global_cache: TTLCache[int, bool] = self._create_cache(ttl=self.rate_limit)
        self._local_cache: dict[int, TTLCache[int, bool]] = {}

    def _create_cache(self, ttl: float) -> TTLCache[int, bool]:
        return TTLCache(maxsize=self.max_size, ttl=ttl)

    def _get_key(self, event: TelegramObject, mode: THROTTLING_MODE) -> int | None:
        if isinstance(event, Message):
            if not event.from_user or not event.chat or not event.bot:
                return None
            match mode:
                case "user":
                    return event.from_user.id
                case "chat":
                    return event.chat.id
                case "bot":
                    return event.bot.id
        elif isinstance(event, CallbackQuery):
            if not event.from_user or not event.message or not event.bot:
                return None
            match mode:
                case "user":
                    return event.from_user.id
                case "chat":
                    return event.message.chat.id
                case "bot":
                    return event.bot.id
        return None

    async def _global_throttling(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        global_key = self._get_key(event, self.mode)
        if global_key is None:
            return await handler(event, data)

        if global_key in self._global_cache:
            return None

        self._global_cache[global_key] = True
        return await handler(event, data)

    async def _local_throttling(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
        *,
        rate: float,
        mode: THROTTLING_MODE,
        handler_id: int,
    ) -> R | None:
        entity_id = self._get_key(event, mode)
        if entity_id is None:
            return await handler(event, data)

        cache = self._local_cache.setdefault(handler_id, self._create_cache(ttl=rate))
        if entity_id in cache:
            return None

        cache[entity_id] = True
        return await handler(event, data)

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        handler_object: HandlerObject | None = data.get("handler")
        if handler_object is None:
            return await handler(event, data)

        event_update: Update | None = data.get("event_update")
        if event_update is not None and event_update.update_id == 0:
            return await handler(event, data)

        limiter_data: dict[str, Any] = handler_object.flags.get("raito__limiter", {})
        local_rate: float | None = limiter_data.get("rate_limit")
        local_mode: THROTTLING_MODE | None = limiter_data.get("mode")

        if local_rate is not None and local_mode is not None:
            handler_id = id(handler_object.callback)
            return await self._local_throttling(
                handler,
                event,
                data,
                rate=local_rate,
                mode=local_mode,
                handler_id=handler_id,
            )
        else:
            return await self._global_throttling(handler, event, data)
