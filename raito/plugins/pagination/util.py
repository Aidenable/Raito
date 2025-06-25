from .enums import PaginationMode
from .paginators.base import BasePaginator
from .paginators.inline import InlinePaginator
from .paginators.text import TextPaginator

__all__ = ("get_paginator",)


def get_paginator(mode: PaginationMode) -> type[BasePaginator]:
    """Get paginator class by mode.

    :param mode: pagination mode
    :type mode: PaginationMode
    :return: paginator class
    :rtype: type[BasePaginator]
    :raises ValueError: if mode is not supported
    """
    if mode == PaginationMode.INLINE:
        return InlinePaginator
    if mode == PaginationMode.TEXT:
        return TextPaginator
    if mode == PaginationMode.MEDIA:
        raise NotImplementedError("Media pagination not implemented yet")

    raise ValueError(f"Unsupported pagination mode: {mode}")
