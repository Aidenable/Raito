from raito.plugins.roles.constraint import RoleConstraint
from raito.plugins.roles.filter import RoleFilter

DUROV = RoleConstraint(
    RoleFilter(
        slug="durov",
        name="Pavel Durov",
        description="Exclusive role for @monk",
        emoji="🔒",
    )
)

EXTENDED_ROLES = [i.filter.data for i in [DUROV]]
EXTENDED_ROLES_BY_SLUG = {role.slug: role for role in EXTENDED_ROLES}
