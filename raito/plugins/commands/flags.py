from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from aiogram.dispatcher.flags import Flag, FlagDecorator

if TYPE_CHECKING:
    from aiogram.utils.i18n.lazy_proxy import LazyProxy  # type: ignore

__all__ = ("description", "hidden", "params")


def description(description: str | LazyProxy) -> FlagDecorator:
    """Attach a description to the command handler for use in command registration (e.g., :code:`raito.register_commands`)

    The description will be shown in the Telegram command list (via :code:`set_my_commands`)
    Supports internationalization via `LazyProxy`.

    :param description: A string or LazyProxy representing the description.
    :return: A FlagDecorator to be applied to the handler.
    """
    return FlagDecorator(Flag("raito__description", value=description))


def hidden(func: Callable) -> Callable[..., Any]:
    """Mark a command handler as hidden from the command list.

    Hidden handlers will not be included in Telegram's slash commands when calling :code:`raito.register_commands`.

    :param func: The command handler to mark as hidden.
    :return: The wrapped handler.
    """
    return FlagDecorator(Flag("raito__hidden", value=True))(func)


def params(**kwargs: type[str] | type[int] | type[bool] | type[float]) -> FlagDecorator:
    """Define expected parameters and their types for command parsing.

    This acts as a lightweight argument extractor and validator for commands.
    For example, :code:`@rt.params(user_id=int)` will extract :code:`user_id=1234` from a command like :code:`/ban 1234`.

    Example:

        .. code-block:: python

            @router.message(filters.Command("ban"))
            @rt.params(user_id=int)
            def ban(message: Message, user_id: int):
                ...

    :param kwargs: A mapping of parameter names to their expected types.
    :return: A FlagDecorator to be applied to the handler with param data.
    """
    return FlagDecorator(Flag("raito__params", value=kwargs))
