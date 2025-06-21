from typing import Protocol, runtime_checkable

from raito.plugins.roles.data import Role

__all__ = ("IRoleProvider",)


@runtime_checkable
class IRoleProvider(Protocol):
    """Protocol for providers that manage user roles."""

    async def get_role(self, bot_id: int, user_id: int) -> Role | None:
        """Get the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :return: The user's role or None if not found
        :rtype: Role | None
        """
        ...

    async def set_role(self, bot_id: int, user_id: int, role: Role) -> None:
        """Set the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :param role: The role to assign
        :type role: Role
        """
        ...

    async def remove_role(self, bot_id: int, user_id: int) -> None:
        """Remove the role for a specific user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        """
        ...

    async def migrate(self) -> None:
        """Initialize the storage backend (create tables, etc.)."""
        ...
