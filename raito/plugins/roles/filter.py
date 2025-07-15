from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram import Bot
from aiogram.filters import Filter
from aiogram.types import TelegramObject, User
from typing_extensions import override

from .data import RoleData

if TYPE_CHECKING:
    from raito.core.raito import Raito

__all__ = ("RoleFilter",)

FLAG_NAME = "raito__roles"


class RoleFilter(Filter):
    """Filter for checking user roles.

    This filter is used to verify whether the user associated with a Telegram event
    has a specific role assigned, such as "admin", "moderator", etc.

    It also attaches role metadata to the handler's flags for use in command registration
    and visualization logic.
    """

    def __init__(
        self,
        slug: str,
        name: str,
        description: str,
        emoji: str,
    ) -> None:
        """Initialize the RoleFilter.

        :param slug: Unique identifier of the role (e.g., "developer")
        :param name: Display name of the role (e.g., "Administrator")
        :param description: Description of the role
        :param emoji: Emoji used to visually represent the role
        """
        self.data = RoleData(slug=slug, name=name, description=description, emoji=emoji)

    @classmethod
    def from_data(cls, data: RoleData) -> RoleFilter:
        """Create a RoleFilter from a RoleData instance.

        :param data: RoleData instance containing role metadata
        :return: A new RoleFilter instance
        """
        return RoleFilter(
            slug=data.slug,
            name=data.name,
            description=data.description,
            emoji=data.emoji,
        )

    @override
    def update_handler_flags(self, flags: dict[str, Any]) -> None:
        """Attach role metadata to handler flags.

        This allows external tools to collect and display role-related constraints.
        """
        roles = flags.setdefault("raito__roles", [])
        roles.append(self.data)

    @override
    async def __call__(
        self,
        event: TelegramObject,
        raito: Raito,
        bot: Bot,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Check if the user in the event has the required role.

        This method is automatically called by aiogram when the filter is used.
        It extracts the user from the event and checks the role manager.

        :param event: Telegram update object (e.g., Message, CallbackQuery)
        :param raito: Raito context object
        :return: Whether the user has the specified role
        :raises RuntimeError: If user could not be resolved from the event
        """
        user = getattr(event, "from_user", None)
        if not isinstance(user, User):
            msg = "Cannot resolve user from TelegramObject"
            raise RuntimeError(msg)

        return await raito.role_manager.has_role(bot.id, user.id, self.data.slug)
