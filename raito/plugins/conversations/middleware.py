from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, TypeVar

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from typing_extensions import override

from raito.utils.helpers.filters import call_filters

from .registry import ConversationRegistry

if TYPE_CHECKING:
    from aiogram.types import TelegramObject

R = TypeVar("R")


__all__ = ("ConversationMiddleware",)


class ConversationMiddleware(BaseMiddleware):
    """Middleware for conversation handling."""

    def __init__(self, registry: ConversationRegistry) -> None:
        """Initialize ConversationMiddleware.

        :param registry: conversation registry
        """
        self.registry = registry

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        """Process message with conversation support.

        :param handler: Next handler in the middleware chain
        :type handler: Callable
        :param event: Telegram event (Message)
        :type event: TelegramObject
        :param data: Additional data passed through the middleware chain
        :type data: dict[str, Any]
        :return: Handler result if not throttled, None if throttled
        """
        if not isinstance(event, Message):
            return await handler(event, data)

        context: FSMContext | None = data.get("state")
        if context is not None:
            state = await context.get_state()
            filters = self.registry.get_filters(context.key)

            if state is None or filters is None:
                return await handler(event, data)

            check = await call_filters(event, data, *filters)
            if not check:
                return await handler(event, data)

            self.registry.resolve(context.key, event)

        return await handler(event, data)
