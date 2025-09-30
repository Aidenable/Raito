import asyncio
from collections.abc import Sequence

from aiogram.dispatcher.event.handler import CallbackType
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from typing_extensions import NamedTuple

__all__ = ("ConversationRegistry",)


class ConversationData(NamedTuple):
    """Container for an active conversation.

    Stores the Future object awaiting a message and the filters to apply.

    :param future: asyncio.Future that will hold the incoming Message
    :param filters: Sequence of CallbackType filters to validate the message
    """

    future: asyncio.Future[Message]
    filters: Sequence[CallbackType]


class ConversationRegistry:
    """Registry for managing active conversations with users.

    This class allows setting up a "wait for message" scenario where
    a handler can pause and wait for a specific message from a user,
    optionally filtered by aiogram filters.
    """

    STATE = "raito__conversation"

    def __init__(self) -> None:
        """Initialize the conversation registry."""
        self._conversations: dict[StorageKey, ConversationData] = {}

    def listen(self, key: StorageKey, *filters: CallbackType) -> asyncio.Future[Message]:
        """Start listening for a message with a specific StorageKey.

        :param key: StorageKey identifying the conversation (user/chat/bot)
        :param filters: Optional filters to apply when the message arrives
        :return: Future that will resolve with the Message when received
        """
        future = asyncio.get_running_loop().create_future()
        self._conversations[key] = ConversationData(future, filters)
        return future

    def get_filters(self, key: StorageKey) -> Sequence[CallbackType] | None:
        """Get the filters associated with an active conversation.

        :param key: StorageKey identifying the conversation
        :return: Sequence of CallbackType filters or None if no conversation exists
        """
        data = self._conversations.get(key)
        return data.filters if data else None

    def resolve(self, key: StorageKey, message: Message) -> None:
        """Complete the conversation with a received message.

        :param key: StorageKey identifying the conversation
        :param message: Message object that satisfies the filters
        """
        data = self._conversations.pop(key, None)
        if data and not data.future.done():
            data.future.set_result(message)

    def cancel(self, key: StorageKey) -> None:
        """Cancel an active conversation.

        Cancels the Future and removes the conversation from the registry.

        :param key: StorageKey identifying the conversation
        """
        data = self._conversations.pop(key, None)
        if data and not data.future.done():
            data.future.cancel()
