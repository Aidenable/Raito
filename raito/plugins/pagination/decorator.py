from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import F, Router

from .data import PaginationCallbackData

if TYPE_CHECKING:
    from aiogram.dispatcher.event.handler import CallbackType

__all__ = ("on_pagination",)


def on_pagination(router: Router, name: str, *filters: CallbackType) -> CallbackType:
    """Register pagination handler for specific name.

    :param router: aiogram router
    :type router: Router
    :param name: pagination name
    :type name: str
    :return: decorator function
    :rtype: CallbackType
    """
    return router.callback_query(
        PaginationCallbackData.filter(F.name == name),
        *filters,
        flags={"raito__is_pagination": True},
    )
