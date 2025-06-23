from dataclasses import dataclass, field
from enum import IntEnum, unique

from pydantic import BaseModel

from raito.plugins.roles.providers.protocol import IRoleProvider

__all__ = (
    "PaginationControls",
    "PaginationLayout",
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
    title_template: str = "{title}"
    counter_template: str = " {current} / {total}"


@unique
class PaginationLayout(IntEnum):
    ARROWS = 0
    COUNTER = 1


@dataclass
class PaginationStyle:
    loop_navigation: bool = True
    controls: PaginationControls = field(default_factory=PaginationControls)
    text_format: PaginationTextFormat = field(default_factory=PaginationTextFormat)
    layout: list[PaginationLayout] = field(
        default_factory=lambda: [PaginationLayout.ARROWS, PaginationLayout.COUNTER]
    )


class RaitoConfiguration(BaseModel):
    router_list_style: RouterListStyle = RouterListStyle.DIAMONDS
    role_provider: IRoleProvider | None = None
    pagination_style: PaginationStyle = PaginationStyle()

    class Config:
        arbitrary_types_allowed = True
