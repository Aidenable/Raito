from __future__ import annotations

from asyncio import sleep
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, TypeVar

from aiogram.dispatcher.event.bases import REJECTED
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache
from typing_extensions import override

if TYPE_CHECKING:
    from aiogram.types import TelegramObject

R = TypeVar("R")


__all__ = ("AlbumMiddleware",)


class AlbumMiddleware(BaseMiddleware):
    """Middleware for album handling."""

    def __init__(
        self,
        delay: float | int = 0.6,
        max_size: int = 10_000,
    ) -> None:
        """Initialize AlbumMiddleware.

        :param flag_name: flag name to filter
        :type flag_name: str
        """
        self.delay = delay
        self._album_data = TTLCache[str, list[Message]](maxsize=max_size, ttl=delay * 5)

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        """Process message with album support.

        :param handler: Next handler in the middleware chain
        :param event: Telegram event (Message or CallbackQuery)
        :param data: Additional data passed through the middleware chain
        :return: Handler result
        """
        if not isinstance(event, Message):
            return await handler(event, data)

        if not event.media_group_id:
            return await handler(event, data)

        if album_data := self._album_data.get(event.media_group_id):
            album_data.append(event)
            return REJECTED

        self._album_data[event.media_group_id] = [event]
        await sleep(self.delay)

        # after sending all media files:
        data["album"] = self._album_data.pop(event.media_group_id)

        return await handler(event, data)
