from raito.plugins.roles.data import Role

from .protocol import IRoleProvider


class MemoryRoleProvider(IRoleProvider):
    """Simple in-memory role provider for testing and development."""

    def __init__(self) -> None:
        """Initialize MemoryRoleProvider."""
        self._roles: dict[int, int] = {}

    async def get_role(self, user_id: int) -> Role | None:
        """Get the role for a specific user.

        :param user_id: The Telegram user ID
        :type user_id: int
        :return: The user's role or None if not found
        :rtype: Role | None
        """
        index = self._roles.get(user_id)
        return Role(index) if index is not None else None

    async def set_role(self, user_id: int, role: Role) -> None:
        """Set the role for a specific user.

        :param user_id: The Telegram user ID
        :type user_id: int
        :param role: The role to assign
        :type role: Role
        """
        self._roles[user_id] = role.value

    async def remove_role(self, user_id: int) -> None:
        """Remove the role for a specific user.

        :param user_id: The Telegram user ID
        :type user_id: int
        """
        self._roles.pop(user_id, None)

    async def migrate(self) -> None:
        """Initialize the storage backend (create tables, etc.)."""
        return
