from enum import IntEnum, unique

__all__ = ("PaginationMode",)


@unique
class PaginationMode(IntEnum):
    """Pagination display modes.

    :cvar INLINE: inline keyboard pagination
    :cvar TEXT: text-based pagination
    :cvar MEDIA: media gallery pagination
    """

    INLINE = 0
    TEXT = 1
    MEDIA = 2
