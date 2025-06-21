from typing import TYPE_CHECKING

from raito.plugins.roles.middleware import RoleMiddleware
from raito.utils import loggers

from .data import Role
from .providers.memory import MemoryRoleProvider
from .providers.protocol import IRoleProvider

if TYPE_CHECKING:
    from aiogram import Dispatcher


__all__ = ("RoleManager",)


class RoleManager:
    """Central manager for role-based access control in Raito."""

    def __init__(self, provider: IRoleProvider, developers: list[int] | None = None) -> None:
        """Initialize RoleManager.

        :param provider: Role provider instance for persistent storage
        :type provider: IRoleProvider
        """
        self.provider = provider
        self._developers = developers

    async def initialize(self, dispatcher: "Dispatcher") -> None:
        """Initialize the RoleManager and run migrations."""
        await self.provider.migrate()

        middleware = RoleMiddleware(flag_name="raito_roles")
        dispatcher.message.middleware(middleware)
        dispatcher.callback_query.middleware(middleware)

        if isinstance(self.provider, MemoryRoleProvider):
            loggers.roles.warn(
                "Using MemoryRoleProvider. It's not recommended for production use.",
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
        return (
            Role.DEVELOPER
            if self.is_developer(user_id)
            else await self.provider.get_role(bot_id, user_id)
        )

    def is_developer(self, user_id: int) -> bool:
        """Check whether the user is a developer.

        Developers are treated as superusers with full permissions.

        :param user_id: The Telegram user ID
        :type user_id: int
        :return: True if user is a developer, False otherwise
        :rtype: bool
        """
        return self._developers is not None and user_id in self._developers

    async def can_manage_roles(self, bot_id: int, user_id: int) -> bool:
        """Check whether the user can manage other users' roles.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :return: True if user can manage roles, False otherwise
        :rtype: bool
        """
        if self.is_developer(user_id):
            return True

        role = await self.get_role(bot_id, user_id)
        return role in (Role.ADMINISTRATOR, Role.OWNER)

    async def _check_role_hierarchy(self, bot_id: int, initiator_id: int, target_id: int) -> None:
        """Check if the initiator can manage the target's role.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param initiator_id: The Telegram user ID of the initiator
        :type initiator_id: int
        :param target_id: The Telegram user ID of the target
        :type target_id: int
        :raises PermissionError: If the initiator cannot manage the target's role
        """
        initiator_role = await self.get_role(bot_id, initiator_id)
        target_role = await self.get_role(bot_id, target_id)

        if initiator_role is None:
            msg = "Cannot determine initiator's current role."
            raise PermissionError(msg)

        if initiator_role != Role.DEVELOPER and target_role and target_role < initiator_role:
            msg = f"Initiator cannot manage roles higher than {initiator_role.name} ({initiator_role.name} < {target_role.name})"
            raise PermissionError(msg)

    async def assign_role(self, bot_id: int, initiator_id: int, target_id: int, role: Role) -> None:
        """Assign a role to a user.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param initiator_id: The Telegram user ID of the initiator
        :type initiator_id: int
        :param target_id: The Telegram user ID of the target
        :type target_id: int
        :param role: The role to assign
        :type role: Role
        :raises PermissionError: If the user does not have permission to assign role
        """
        if initiator_id == target_id:
            msg = "You cannot assign your own role."
            raise PermissionError(msg)

        if not await self.can_manage_roles(bot_id, initiator_id):
            msg = "You do not have permission to assign roles."
            raise PermissionError(msg)

        if role == Role.DEVELOPER:
            msg = "You cannot assign the Developer role."
            raise PermissionError(msg)

        await self._check_role_hierarchy(bot_id, initiator_id, target_id)
        await self.provider.set_role(bot_id, target_id, role)

    async def revoke_role(self, bot_id: int, initiator_id: int, target_id: int) -> None:
        """Revoke a user's role.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param initiator_id: The Telegram user ID of the initiator
        :type initiator_id: int
        :param target_id: The Telegram user ID of the target
        :type target_id: int
        :raises PermissionError: If the user does not have permission to revoke roles
        """
        if initiator_id == target_id:
            msg = "You cannot revoke your own role."
            raise PermissionError(msg)

        if not await self.can_manage_roles(bot_id, initiator_id):
            msg = "You do not have permission to assign roles."
            raise PermissionError(msg)

        await self._check_role_hierarchy(bot_id, initiator_id, target_id)
        await self.provider.remove_role(bot_id, target_id)

    async def has_any_roles(
        self,
        bot_id: int,
        user_id: int,
        *roles: Role,
        allow_developers: bool = True,
    ) -> bool:
        """Check if a user has any of the specified roles.

        :param bot_id: The Telegram bot ID
        :type bot_id: int
        :param user_id: The Telegram user ID
        :type user_id: int
        :param roles: Roles to check for
        :type roles: Role
        :param allow_developers: Whether to allow developers to have roles
        :type allow_developers: bool
        :returns: True if user has any of the roles, False otherwise
        :rtype: bool
        """
        if self.is_developer(user_id) and allow_developers:
            return True

        role = await self.get_role(bot_id, user_id)
        return role in roles
