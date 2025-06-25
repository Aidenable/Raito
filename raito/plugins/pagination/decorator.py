from aiogram import F, Router
from aiogram.dispatcher.event.handler import CallbackType

from .data import PaginationCallbackData

__all__ = ("on_pagination",)


def on_pagination(router: Router, name: str) -> CallbackType:
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
        flags={"is_pagination": True},
    )
