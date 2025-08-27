from __future__ import annotations

import contextlib
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, TypeVar

from aiogram import Bot
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram.types.update import Update
from typing_extensions import override

from raito.plugins.pagination.data import PaginationCallbackData
from raito.plugins.pagination.enums import PaginationMode
from raito.plugins.pagination.util import get_paginator

from .paginators.base import BasePaginator

if TYPE_CHECKING:
    from aiogram.types import TelegramObject

    from raito import Raito

R = TypeVar("R")


__all__ = ("PaginatorMiddleware",)


class PaginatorMiddleware(BaseMiddleware):
    """Middleware for pagination handling."""

    def __init__(self, flag_name: str = "raito__is_pagination") -> None:
        """Initialize pagination middleware.

        :param flag_name: flag name to filter
        :type flag_name: str
        """
        self.flag_name = flag_name

    def _extract_required_data(self, data: dict[str, Any]) -> tuple[Update, Raito, Bot]:
        """Extract required data from middleware context.

        :param data: middleware data
        :type data: dict[str, Any]
        :return: tuple of update, raito and bot
        :rtype: tuple[Update, Raito, Bot]
        :raises ValueError: if required data is missing
        """
        event_update = data.get("event_update")
        if not event_update:
            raise ValueError("Event update not found")

        raito = data.get("raito")
        if not raito:
            raise ValueError("Raito instance not found")

        bot = data.get("bot")
        if not bot:
            raise ValueError("Bot instance not found")

        return event_update, raito, bot

    def _validate_callback_query(self, query: CallbackQuery, event_update: Update) -> str:
        """Validate callback query data.

        :param query: callback query
        :type query: CallbackQuery
        :param event_update: update event
        :type event_update: Update
        :return: callback data string
        :rtype: str
        :raises ValueError: if callback query is invalid
        """
        if not event_update.callback_query or not event_update.callback_query.data:
            raise ValueError("Callback query data not found")

        if not isinstance(query.message, Message):
            raise ValueError("Message not accessible")

        return event_update.callback_query.data

    def _create_paginator(self, query: CallbackQuery, data: dict[str, Any]) -> BasePaginator:
        """Create paginator instance from callback data.

        :param query: callback query
        :type query: CallbackQuery
        :param data: middleware data
        :type data: dict[str, Any]
        :return: paginator instance
        :rtype: BasePaginator
        """
        event_update, raito, bot = self._extract_required_data(data)

        if not event_update.callback_query or not event_update.callback_query.data:
            raise ValueError("Callback query data not found")

        if not isinstance(query.message, Message):
            raise ValueError("Message not accessible")

        callback_data = PaginationCallbackData.unpack(event_update.callback_query.data)
        Paginator = get_paginator(PaginationMode(callback_data.mode))
        return Paginator(
            raito=raito,
            name=callback_data.name,
            chat_id=query.message.chat.id,
            bot=bot,
            from_user=query.from_user,
            existing_message=query.message,
            current_page=callback_data.current_page,
            total_pages=callback_data.total_pages,
            limit=callback_data.limit,
        )

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        """Process callback_query with pagination support.

        :param handler: Next handler in the middleware chain
        :type handler: Callable
        :param event: Telegram event (Message or CallbackQuery)
        :type event: TelegramObject
        :param data: Additional data passed through the middleware chain
        :type data: dict[str, Any]
        :return: Handler result if not throttled, None if throttled
        """
        handler_object: HandlerObject | None = data.get("handler")
        if handler_object is None:
            raise RuntimeError("Handler object not found")

        is_pagination = handler_object.flags.get(self.flag_name, False)
        if not is_pagination:
            return await handler(event, data)

        if not isinstance(event, CallbackQuery):
            return await handler(event, data)

        with contextlib.suppress(TelegramBadRequest):
            await event.answer()

        paginator: BasePaginator | None = data.get("paginator")
        if not paginator:
            paginator = self._create_paginator(event, data)

        if isinstance(event.message, Message):
            paginator.chat_id = event.message.chat.id

        bot: Bot | None = data.get("bot")
        if bot is not None:
            paginator.bot = bot

        data["paginator"] = paginator
        data["page"] = paginator.current_page
        data["offset"] = (paginator.current_page - 1) * paginator.limit
        data["limit"] = paginator.limit

        return await handler(event, data)
