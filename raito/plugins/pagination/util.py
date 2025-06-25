from raito.plugins.pagination.enums import PaginationMode
from raito.plugins.pagination.paginators.base import BasePaginator
from raito.plugins.pagination.paginators.inline import InlinePaginator

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
        raise NotImplementedError("Text pagination not implemented yet")
    if mode == PaginationMode.MEDIA:
        raise NotImplementedError("Media pagination not implemented yet")

    raise ValueError(f"Unsupported pagination mode: {mode}")
