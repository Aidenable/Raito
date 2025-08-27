from dataclasses import dataclass, field
from enum import IntEnum, unique

from pydantic import BaseModel

from raito.plugins.roles.manager import RoleManager

__all__ = (
    "PaginationControls",
    "PaginationStyle",
    "PaginationTextFormat",
    "RaitoConfiguration",
    "RouterListStyle",
)


@unique
class RouterListStyle(IntEnum):
    SQUARES = 0
    CIRCLES = 1
    DIAMONDS = 2
    DIAMONDS_REVERSED = 3


@dataclass
class PaginationControls:
    previous: str = "◀️"
    next: str = "▶️"


@dataclass
class PaginationTextFormat:
    counter_template: str = "{current} / {total}"


@dataclass
class PaginationStyle:
    loop_navigation: bool = True
    controls: PaginationControls = field(default_factory=PaginationControls)
    text_format: PaginationTextFormat = field(default_factory=PaginationTextFormat)
    show_counter: bool = True


class RaitoConfiguration(BaseModel):
    router_list_style: RouterListStyle = RouterListStyle.DIAMONDS
    role_manager: RoleManager | None = None
    pagination_style: PaginationStyle = PaginationStyle()

    class Config:
        arbitrary_types_allowed = True
