from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar

from aiogram.dispatcher.event.bases import REJECTED
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.filters.command import CommandObject
from aiogram.types import Message, TelegramObject
from typing_extensions import override

from raito.utils.helpers.command_help import get_command_help

if TYPE_CHECKING:
    from raito.core.raito import Raito

DataT = TypeVar("DataT", bound=dict[str, Any])
R = TypeVar("R")
ParamT: TypeAlias = type[int] | type[str] | type[bool] | type[float]


__all__ = ("CommandMiddleware",)


class CommandMiddleware(BaseMiddleware):
    """Middleware for command-related features.

    - Supports automatic parameter parsing from text based on the :code:`raito__params` flag.

    *Can be extended with additional logic in the future*
    """

    def __init__(self) -> None:
        """Initialize CommandMiddleware."""

    def _unpack_params(
        self,
        command: CommandObject,
        params: dict[str, ParamT],
        data: DataT,
    ) -> DataT:
        """Unpack command parameters into the metadata.

        :param handler_object: Handler object
        :param event: Telegram message
        :param data: Current metadata
        :return: Updated context with parsed parameters
        :raises ValueError, IndexError: If parameter is missing or invalid
        """
        args = command.args.split() if command.args else []
        for i, (key, value_type) in enumerate(params.items()):
            arg = args[i]
            if value_type is bool:
                bool_value: bool = arg.lower() in ("true", "yes", "on", "1", "ok", "+")
                data[key] = bool_value
            else:
                data[key] = value_type(arg)

        return data

    async def _send_help_message(
        self,
        handler_object: HandlerObject,
        command: CommandObject,
        params: dict[str, ParamT],
        event: Message,
        data: dict[str, Any],
    ) -> None:
        description = handler_object.flags.get("raito__description")
        raito: Raito | None = data.get("raito")

        if raito is not None and raito.command_parameters_error.handlers:
            target = {"handler": handler_object, "command": command}
            await raito.command_parameters_error.trigger(event, target=target)
        else:
            await event.reply(
                get_command_help(command, params, description=description),
                parse_mode="HTML",
            )

    @override
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
            return await handler(event, data)

        command: CommandObject | None = data.get("command")
        if command is None:
            return await handler(event, data)

        params: dict[str, ParamT] | None = handler_object.flags.get("raito__params")
        if params:
            try:
                data = self._unpack_params(command, params, data)
            except (ValueError, IndexError):
                await self._send_help_message(handler_object, command, params, event, data)
                return REJECTED

        return await handler(event, data)
