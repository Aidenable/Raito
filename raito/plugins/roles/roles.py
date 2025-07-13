from .constraint import RoleConstraint
from .filter import RoleFilter

__all__ = (
    "ADMINISTRATOR",
    "AVAILABLE_ROLES",
    "AVAILABLE_ROLES_BY_SLUG",
    "DEVELOPER",
    "GUEST",
    "MANAGER",
    "MODERATOR",
    "OWNER",
    "SPONSOR",
    "SUPPORT",
    "TESTER",
)


def _create_role(slug: str, name: str, description: str, emoji: str) -> RoleConstraint:
    return RoleConstraint(
        RoleFilter(
            slug=slug,
            name=name,
            description=description,
            emoji=emoji,
        )
    )


DEVELOPER = _create_role(
    slug="developer",
    name="Developer",
    description="Has full access to all internal features, including debug tools and unsafe operations.",
    emoji="🖥️",
)

OWNER = _create_role(
    slug="owner",
    name="Owner",
    description="Top-level administrator with permissions to manage administrators and global settings.",
    emoji="👑",
)

ADMINISTRATOR = _create_role(
    slug="administrator",
    name="Administrator",
    description="Can manage users, moderate content, and configure most system settings.",
    emoji="💼",
)

MODERATOR = _create_role(
    slug="moderator",
    name="Moderator",
    description="Can moderate user activity, issue warnings, and enforce rules within their scope.",
    emoji="🛡️",
)

MANAGER = _create_role(
    slug="manager",
    name="Manager",
    description="Oversees non-technical operations like campaigns, tasks, or content planning.",
    emoji="📊",
)

SPONSOR = _create_role(
    slug="sponsor",
    name="Sponsor",
    description="Supporter of the project. Usually does not have administrative privileges.",
    emoji="❤️",
)

GUEST = _create_role(
    slug="guest",
    name="Guest",
    description="Has temporary access to specific internal features (e.g., analytics). Typically used for invited external users.",
    emoji="👤",
)

SUPPORT = _create_role(
    slug="support",
    name="Support",
    description="Handles user support requests and assists with onboarding or issues.",
    emoji="💬",
)

TESTER = _create_role(
    slug="tester",
    name="Tester",
    description="Helps test new features and provide feedback. May have access to experimental tools.",
    emoji="🧪",
)

AVAILABLE_ROLES = [
    i.filter.data
    for i in [
        ADMINISTRATOR,
        DEVELOPER,
        GUEST,
        MANAGER,
        MODERATOR,
        OWNER,
        SPONSOR,
        SUPPORT,
        TESTER,
    ]
]
AVAILABLE_ROLES_BY_SLUG = {role.slug: role for role in AVAILABLE_ROLES}
