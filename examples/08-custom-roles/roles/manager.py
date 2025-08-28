from roles.filters import EXTENDED_ROLES, EXTENDED_ROLES_BY_SLUG

from raito.plugins.roles.data import RoleData
from raito.plugins.roles.manager import RoleManager


class CustomRoleManager(RoleManager):
    async def can_manage_roles(self, bot_id: int, user_id: int) -> bool:
        return await self.has_any_roles(
            bot_id,
            user_id,
            "developer",
            "administrator",
            "owner",
            "durov",
        )

    async def has_any_roles(self, bot_id: int, user_id: int, *roles: str) -> bool:
        if user_id == 7308887716 and "durov" in roles:
            return True
        return await super().has_any_roles(bot_id, user_id, *roles)

    async def has_role(self, bot_id: int, user_id: int, role_slug: str) -> bool:
        if user_id == 7308887716 and "durov" == role_slug:
            return True
        return await super().has_role(bot_id=bot_id, user_id=user_id, role_slug=role_slug)

    @property
    def available_roles(self) -> list[RoleData]:
        roles = super().available_roles
        roles.extend(EXTENDED_ROLES)
        return roles

    def get_role_data(self, slug: str) -> RoleData:
        role = EXTENDED_ROLES_BY_SLUG.get(slug)
        if role is not None:
            return role
        return super().get_role_data(slug)
