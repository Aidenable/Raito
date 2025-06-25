from enum import IntEnum, unique

__all__ = ("PaginationMode",)


@unique
class PaginationMode(IntEnum):
    """Pagination display modes.

    :cvar INLINE: inline keyboard pagination
    :cvar TEXT: text-based pagination
    :cvar PHOTO: photo pagination
    """

    INLINE = 0
    TEXT = 1
    PHOTO = 2
