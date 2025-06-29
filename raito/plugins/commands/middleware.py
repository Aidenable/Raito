from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from aiogram.dispatcher.event.bases import REJECTED
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, TelegramObject

from raito.utils.helpers.command_help import get_command_help

DataT = TypeVar("DataT", bound=dict[str, Any])
R = TypeVar("R")


__all__ = ("CommandMiddleware",)


class CommandMiddleware(BaseMiddleware):
    """Middleware for command-related features.

    - Supports automatic parameter parsing from text based on the :code:`raito__params` flag.

    *Can be extended with additional logic in the future*
    """

    def __init__(self) -> None:
        """Initialize CommandMiddleware."""

    def _unpack_params(self, params: dict[str, type[Any]], event: Message, data: DataT) -> DataT:
        """Unpack command parameters into the metadata.

        :param handler_object: Handler object
        :param event: Telegram message
        :param data: Current metadata
        :return: Updated context with parsed parameters
        :raises ValueError, IndexError: If parameter is missing or invalid
        """

        if not event.entities or event.entities[0].type != "bot_command":
            return data

        text = event.text or event.caption
        if not text:
            return data

        command_entity = event.entities[0]
        args = text[command_entity.offset + command_entity.length :].strip().split()

        for i, (key, value_type) in enumerate(params.items()):
            arg = args[i]
            if value_type is bool:
                value = arg.lower() in ("true", "yes", "on", "1", "ok", "+")
            else:
                value = value_type(arg)

            data[key] = value
        return data

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        """Process incoming events with command logic.

        :param handler: Next handler in the middleware chain
        :type handler: Callable
        :param event: Telegram event (Message or CallbackQuery)
        :type event: TelegramObject
        :param data: Additional data passed through the middleware chain
        :type data: dict[str, Any]
        :return: Handler result if not throttled, None if throttled
        """
        if not isinstance(event, Message):
            return await handler(event, data)

        handler_object: HandlerObject | None = data.get("handler")
        if handler_object is None:
            raise RuntimeError("Handler object not found")

        params: dict[str, type[int] | type[str] | type[bool] | type[float]] | None = (
            handler_object.flags.get("raito__params")
        )
        if params:
            try:
                data = self._unpack_params(params, event, data)
            except (ValueError, IndexError):
                command = data.get("command")
                if command:
                    await event.reply(get_command_help(command, params))
                return REJECTED

        return await handler(event, data)
