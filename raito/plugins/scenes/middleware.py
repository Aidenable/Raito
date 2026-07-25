from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, TypeVar

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from typing_extensions import override

if TYPE_CHECKING:
    from aiogram.types import TelegramObject

    from .manager import SceneManager

R = TypeVar("R")

__all__ = ("SceneMiddleware",)


class SceneMiddleware(BaseMiddleware):
    """Middleware that drops a stale scene before its step runs.

    Installed on both the message and callback query observers, so a stale scene
    is dropped whether the next step expects text or an inline button.
    """

    def __init__(self, manager: SceneManager[Any]) -> None:
        """Initialize SceneMiddleware.

        :param manager: scene this middleware clears stale state for
        """
        self.manager = manager

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        """Clear a stale scene before the next handler runs.

        :param handler: next handler in the middleware chain
        :param event: incoming Telegram event
        :param data: contextual data passed through the chain
        :return: handler result
        """
        if not isinstance(event, Message | CallbackQuery):
            return await handler(event, data)

        if await self.manager.cleanup(data.get("state"), data.get("raw_state")):
            data["raw_state"] = None
            if isinstance(event, CallbackQuery):
                await event.answer()

        return await handler(event, data)
