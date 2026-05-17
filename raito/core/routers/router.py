from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from aiogram import Router as AiogramRouter
from aiogram.dispatcher.event.event import EventObserver

from raito.plugins.lifespan.decorator import FuncType, lifespan
from raito.plugins.pagination.decorator import on_pagination

if TYPE_CHECKING:
    from aiogram.dispatcher.event.handler import CallbackType

    from raito.core.raito import Raito

__all__ = ("Router",)


class Router(AiogramRouter):
    """An expanded aiogram router implementation."""

    _command_signature_error = EventObserver()

    def __init__(
        self,
        *,
        name: str | None = None,
        priority: int = 0,
        autoload: bool = True,
    ) -> None:
        """Initialize the Raito Router.

        :param name: Optional router name
        :type name: str | None
        :param priority: Router priority when loading, default is 0
        :type priority: int
        :param autoload: Auto-load routers on startup
        :type autoload: bool
        """
        super().__init__(name=name)
        self.priority = priority
        self.autoload = autoload

        self._raito: Raito | None = None

    def on_pagination(self, name: str, *filters: CallbackType) -> CallbackType:
        """Register pagination handler for specific name.

        :param name: pagination name
        :type name: str
        :return: decorator function
        :rtype: CallbackType
        """
        return on_pagination(self, name, *filters)

    def on_command_signature_error(self) -> Callable[[CallbackType], CallbackType]:
        """Called when the signature of an entered command is incorrect.

        Example:

           .. code-block:: python

              @router.on_command_signature_error()
              async def handler(event, command, params, description) -> None:
                  await event.reply(get_command_help(command, params, description))

        :param event: Message event
        :type event: Message
        :param handler: Handler object
        :type handler: HandlerObject
        :param command: Command object
        :type command: CommandObject
        :param params: Command parameters
        :type params: dict[str, int | str | bool | float]
        :param description: Optional command description
        :type description: str | None
        :rtype: CallbackType
        """
        return self._command_signature_error()

    def lifespan(self) -> Callable[[FuncType], FuncType]:
        """
        Register a lifespan function for a given router, similar to FastAPI's lifespan handler.
        The function must be an async generator: it runs setup before `yield`, and cleanup after.
        """
        return lifespan(self)
