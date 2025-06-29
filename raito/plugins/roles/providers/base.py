from asyncio import Lock

from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder, StorageKey

from raito.plugins.roles.data import Role

from .protocol import IRoleProvider

__all__ = ("BaseRoleProvider",)


class BaseRoleProvider(IRoleProvider):
    """Base role provider class."""

    def __init__(self, storage: BaseStorage) -> None:
        """Initialize BaseRoleProvider."""
        self.storage = storage
        self.key_builder = DefaultKeyBuilder(with_destiny=True, with_bot_id=True)
        self._lock = Lock()

    def _build_key(self, *, bot_id: int) -> StorageKey:
        """Build a storage key for a specific bot.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :return: The storage key
        :rtype: StorageKey
        """
        return StorageKey(  # applies to a single bot across all chats
            bot_id=bot_id,
            chat_id=0,
            user_id=0,
            destiny="roles",
        )

    async def get_role(self, bot_id: int, user_id: int) -> Role | None:
        """Get the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :return: The user's role or None if not found
        :rtype: Role | None
        """
        key = self._build_key(bot_id=bot_id)
        data: dict[str, int] = await self.storage.get_data(key)
        index = data.get(str(user_id))
        return Role(index) if index is not None else None

    async def set_role(self, bot_id: int, user_id: int, role: Role) -> None:
        """Set the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :param role: The role to assign
        :type role: Role
        """
        key = self._build_key(bot_id=bot_id)
        async with self._lock:
            data: dict[str, int] = await self.storage.get_data(key)
            data[str(user_id)] = role.value
            await self.storage.set_data(key, data)

    async def remove_role(self, bot_id: int, user_id: int) -> None:
        """Remove the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        """
        key = self._build_key(bot_id=bot_id)
        async with self._lock:
            data: dict[str, int] = await self.storage.get_data(key)
            data.pop(str(user_id), None)
            await self.storage.set_data(key, data)

    async def migrate(self) -> None:
        """Initialize the storage backend (create tables, etc.)."""
        return

    async def get_users(self, bot_id: int, role: Role) -> list[int]:
        """Get all users with a specific role.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param role: The role to check for
        :type role: Role
        :return: A list of Telegram user IDs
        :rtype: list[int]
        """
        key = self._build_key(bot_id=bot_id)
        async with self._lock:
            data: dict[str, int] = await self.storage.get_data(key)
            return [int(user_id) for user_id, user_role in data.items() if user_role == role.value]
