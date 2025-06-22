from enum import IntEnum, unique

from pydantic import BaseModel

from raito.plugins.roles import IRoleProvider

__all__ = ("Configuration",)


class Configuration(BaseModel):
    """Raito configuration."""

    @unique
    class RouterListStyle(IntEnum):
        """Style for `.rt list` command."""

        SQUARES = 0
        CIRCLES = 1
        RHOMBUSES = 2
        RHOMBUSES_REVERSED = 3

    router_list_style: RouterListStyle = RouterListStyle.RHOMBUSES
    role_provider: IRoleProvider | None = None

    class Config:
        """Pydantic settings."""

        arbitrary_types_allowed = True
