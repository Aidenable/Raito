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

    def _build_key(self, *, bot_id: int, user_id: int) -> StorageKey:
        """Build a storage key for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :return: The storage key
        :rtype: StorageKey
        """
        return StorageKey(  # role applies to a single bot across all chats
            bot_id=bot_id,
            chat_id=user_id,
            user_id=user_id,
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
        key = self._build_key(bot_id=bot_id, user_id=user_id)
        index = await self.storage.get_value(key, "role")
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
        key = self._build_key(bot_id=bot_id, user_id=user_id)
        await self.storage.update_data(key, {"role": role.value})

    async def remove_role(self, bot_id: int, user_id: int) -> None:
        """Remove the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        """
        key = self._build_key(bot_id=bot_id, user_id=user_id)
        await self.storage.update_data(key, {"role": None})

    async def migrate(self) -> None:
        """Initialize the storage backend (create tables, etc.)."""
        return
