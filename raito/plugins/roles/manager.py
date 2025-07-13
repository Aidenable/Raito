from __future__ import annotations

from raito.plugins.roles.data import RoleData

from .providers.protocol import IRoleProvider
from .roles import AVAILABLE_ROLES, AVAILABLE_ROLES_BY_SLUG

__all__ = ("RoleManager",)


class RoleManager:
    """Central manager for role-based access control in Raito."""

    def __init__(self, provider: IRoleProvider, developers: list[int] | None = None) -> None:
        """Initialize RoleManager.

        :param provider: Role provider instance for persistent storage
        :type provider: IRoleProvider
        """
        self.provider = provider
        self.developers = developers or []

    async def migrate(self) -> None:
        """Run provider migrations."""
        await self.provider.migrate()

    async def get_role(self, bot_id: int, user_id: int) -> str | None:
        """Get the role for a specific user.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        :return: The role slug or None if not found
        """
        return await self.provider.get_role(bot_id, user_id)

    async def can_manage_roles(self, bot_id: int, user_id: int) -> bool:
        """Check whether the user can manage other users' roles.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        :return: True if user can manage roles, False otherwise
        """
        return await self.has_any_roles(
            bot_id,
            user_id,
            "developer",
            "administrator",
            "owner",
        )

    async def assign_role(
        self,
        bot_id: int,
        initiator_id: int,
        target_id: int,
        role_slug: str,
    ) -> None:
        """Assign a role to a user.

        :param bot_id: The Telegram bot ID
        :param initiator_id: The Telegram user ID of the initiator
        :param target_id: The Telegram user ID of the target
        :param role_slug: The role to assign
        :raises PermissionError: If the user does not have permission to assign role
        """
        if initiator_id == target_id:
            msg = "You cannot assign your own role."
            raise PermissionError(msg)

        if not await self.can_manage_roles(bot_id, initiator_id):
            msg = "You do not have permission to assign roles."
            raise PermissionError(msg)

        await self.provider.set_role(bot_id, target_id, role_slug)

    async def revoke_role(self, bot_id: int, initiator_id: int, target_id: int) -> None:
        """Revoke a user's role.

        :param bot_id: The Telegram bot ID
        :param initiator_id: The Telegram user ID of the initiator
        :param target_id: The Telegram user ID of the target
        :raises PermissionError: If the user does not have permission to revoke roles
        """
        if initiator_id == target_id:
            msg = "You cannot revoke your own role."
            raise PermissionError(msg)

        if not await self.can_manage_roles(bot_id, initiator_id):
            msg = "You do not have permission to assign roles."
            raise PermissionError(msg)

        await self.provider.remove_role(bot_id, target_id)

    async def has_any_roles(self, bot_id: int, user_id: int, *roles: str) -> bool:
        """Check if a user has any of the specified roles.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        :param roles: Roles to check for
        :returns: True if user has any of the roles, False otherwise
        """
        if user_id in self.developers and "developer" in roles:
            return True

        role = await self.get_role(bot_id, user_id)
        return role in roles

    async def has_role(self, bot_id: int, user_id: int, role_slug: str) -> bool:
        """Check if a user has the specified roles.

        :param bot_id: The Telegram bot ID
        :param user_id: The Telegram user ID
        :param role_slug: Role to check for
        :returns: True if user has the role, False otherwise
        """
        if user_id in self.developers and role_slug == "developer":
            return True

        slug = await self.get_role(bot_id, user_id)
        return slug == role_slug

    async def get_users(self, bot_id: int, role: str) -> set[int]:
        """Get a list of users with a specific role.

        :param bot_id: The Telegram bot ID
        :param role: The role to check for
        :returns: A list of Telegram user IDs
        """
        users = await self.provider.get_users(bot_id, role)
        unique_users = set(users)

        if role == "developer":
            unique_users.update(self.developers)

        return unique_users

    @property
    def available_roles(self) -> list[RoleData]:
        """Get a list of available roles.

        :returns: A list of roles
        """
        return AVAILABLE_ROLES

    def get_role_data(self, slug: str) -> RoleData:
        """Get data of specified role.

        :returns: A data of role
        :raises: ...
        """
        return AVAILABLE_ROLES_BY_SLUG[slug]
