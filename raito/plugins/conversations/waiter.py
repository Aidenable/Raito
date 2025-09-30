from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiogram.dispatcher.event.handler import CallbackType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from typing_extensions import Any

if TYPE_CHECKING:
    from raito import Raito

__all__ = ("Waiter", "wait_for")


@dataclass
class Waiter:
    """Container for conversation result.

    :param text: Raw text of the message
    :param number: Parsed integer if ``text`` is a digit, otherwise ``None``
    :param message: Original :class:`aiogram.types.Message` object
    :param retry: Callable coroutine for repeating the same wait
    """

    text: str
    number: int | None
    message: Message
    retry: Callable[[], Coroutine[Any, Any, Waiter]]


async def wait_for(
    raito: Raito,
    context: FSMContext,
    *filters: CallbackType,
) -> Waiter:
    """Wait for the next message from user that matches given filters.

    This function sets special state ``raito__conversation`` in FSM and
    suspends coroutine execution until user sends a message that passes
    all provided filters. Result is wrapped into :class:`Waiter`.

    :param raito: Current :class:`Raito` instance
    :param context: FSM context for current chat
    :param filters: Sequence of aiogram filters
    :return: Conversation result with text, parsed number and original message
    :raises RuntimeError: If handler object not found during filter execution
    :raises asyncio.CancelledError: If conversation was cancelled
    """
    await context.set_state(raito.registry.STATE)
    message = await raito.registry.listen(context.key, *filters)

    async def retry() -> Waiter:
        return await wait_for(raito, context, *filters)

    text = message.text or message.caption or ""
    return Waiter(
        text=text,
        number=int(text) if text.isdigit() else None,
        message=message,
        retry=retry,
    )
