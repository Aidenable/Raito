from typing import Protocol, runtime_checkable

__all__ = ("IRoleProvider",)


@runtime_checkable
class IRoleProvider(Protocol):
    """Protocol for providers that manage user roles."""

    async def get_role(self, bot_id: int, user_id: int) -> str | None:
        """Get the role for a specific user.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        :return: The role slug or None if not found
        """
        ...

    async def set_role(self, bot_id: int, user_id: int, role_slug: str) -> None:
        """Set the role for a specific user.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        :param role_slug: The role slug to assign
        """
        ...

    async def remove_role(self, bot_id: int, user_id: int) -> None:
        """Remove the role for a specific user.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        """
        ...

    async def migrate(self) -> None:
        """Initialize the storage backend (create tables, etc.)."""
        ...

    async def get_users(self, bot_id: int, role_slug: str) -> list[int]:
        """Get all users with a specific role.

        :param bot_id: The Telegram bot ID
        :param role_slug: The role slug to check for
        :return: A list of Telegram user IDs
        """
        ...
