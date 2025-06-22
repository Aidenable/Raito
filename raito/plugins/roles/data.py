from dataclasses import dataclass
from enum import IntEnum

__all__ = (
    "ROLES_DATA",
    "Role",
    "RoleData",
)


@dataclass
class RoleData:
    """Data for a role."""

    emoji: str
    name: str
    description: str


ROLES_DATA: dict[int, RoleData] = {
    0: RoleData(
        emoji="🖥️",
        name="Developer",
        description="Has full access to all internal features, including debug tools and unsafe operations.",
    ),
    1: RoleData(
        emoji="👑",
        name="Owner",
        description="Top-level administrator with permissions to manage administrators and global settings.",
    ),
    2: RoleData(
        emoji="💼",
        name="Administrator",
        description="Can manage users, moderate content, and configure most system settings.",
    ),
    3: RoleData(
        emoji="🛡️",
        name="Moderator",
        description="Can moderate user activity, issue warnings, and enforce rules within their scope.",
    ),
    4: RoleData(
        emoji="📊",
        name="Manager",
        description="Oversees non-technical operations like campaigns, tasks, or content planning.",
    ),
    5: RoleData(
        emoji="❤️",
        name="Sponsor",
        description="Supporter of the project. Usually does not have administrative privileges.",
    ),
    6: RoleData(
        emoji="👤",
        name="Guest",
        description="Has temporary access to specific internal features (e.g., analytics). Typically used for invited external users.",
    ),
    7: RoleData(
        emoji="💬",
        name="Support",
        description="Handles user support requests and assists with onboarding or issues.",
    ),
    8: RoleData(
        emoji="🧪",
        name="Tester",
        description="Helps test new features and provide feedback. May have access to experimental tools.",
    ),
}


class Role(IntEnum):
    """Various user roles in the Raito implementation."""

    DEVELOPER = 0
    OWNER = 1
    ADMINISTRATOR = 2
    MODERATOR = 3
    MANAGER = 4
    SPONSOR = 5
    GUEST = 6
    SUPPORT = 7
    TESTER = 8

    @property
    def data(self) -> RoleData | None:
        """Returns the data of the role."""
        return ROLES_DATA.get(self.value)

    @property
    def label(self) -> str:
        """Returns emoji and name of the role."""
        return f"{self.emoji} {self.name}"

    @property
    def emoji(self) -> str:
        """Returns the emoji of the role."""
        return self.data.emoji if self.data else ""

    @property
    def name(self) -> str:
        """Returns the name of the role."""
        return self.data.name if self.data else ""

    @property
    def description(self) -> str:
        """Returns the description of the role."""
        return self.data.description if self.data else ""
