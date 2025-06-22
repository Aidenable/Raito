from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, TypeVar

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

if TYPE_CHECKING:
    from aiogram.dispatcher.event.handler import HandlerObject

    from raito.core.raito import Raito

R = TypeVar("R")


__all__ = ("RoleMiddleware",)


class RoleMiddleware(BaseMiddleware):
    """Middleware for checking user roles.

    Check is based on Aiogram's built-in flags.
    """

    def __init__(self, flag_name: str) -> None:
        """Initialize RolesMiddleware.

        :param flag_name: Name of the flag to check
        :type max_size: str, optional
        """
        self.flag_name = flag_name

    async def _answer(self, event: TelegramObject, text: str) -> None:
        """Send a message to the user.

        :param event: Telegram event (Message or CallbackQuery)
        :type event: TelegramObject
        :param text: Message text
        :type text: str
        """
        if isinstance(event, Message):
            await event.reply(text)
        elif isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[R]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> R | None:
        """Process incoming events with role checking logic.

        Checks if the user has the required role to access the event.
        If not, sends a message and returns None to skip processing.

        :param handler: Next handler in the middleware chain
        :type handler: Callable
        :param event: Telegram event (Message or CallbackQuery)
        :type event: TelegramObject
        :param data: Additional data passed through the middleware chain
        :type data: dict[str, Any]
        :return: Handler result if not throttled, None if throttled
        """
        user_id: int

        if isinstance(event, Message | CallbackQuery) and event.from_user and event.bot:
            user_id = event.from_user.id
        else:
            return await handler(event, data)

        raito: Raito | None = data.get("raito")
        if not raito:
            msg = "Raito is not initialized."
            raise RuntimeError(msg)

        handler_object: HandlerObject | None = data.get("handler")
        if not handler_object:
            msg = "Handler object is not found."
            raise RuntimeError(msg)

        roles = handler_object.flags.get(self.flag_name, [])
        if roles and not await raito.role_manager.has_any_roles(event.bot.id, user_id, *roles):
            await self._answer(event, "🚫 Access denied")
            return None

        return await handler(event, data)
