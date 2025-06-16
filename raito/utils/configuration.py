from enum import IntEnum, unique

from pydantic import BaseModel


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
