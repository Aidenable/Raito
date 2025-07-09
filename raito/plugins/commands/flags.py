from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from aiogram.dispatcher.flags import Flag, FlagDecorator

if TYPE_CHECKING:
    from aiogram.utils.i18n.lazy_proxy import LazyProxy  # type: ignore

__all__ = ("description", "hidden", "params")


def description(description: str | LazyProxy) -> FlagDecorator:
    return FlagDecorator(Flag("raito__description", value=True))(description)


def hidden(func: Callable) -> Callable[..., Any]:
    return FlagDecorator(Flag("raito__hidden", value=True))(func)


def params(**kwargs: type[str] | type[int] | type[bool] | type[float]) -> FlagDecorator:
    return FlagDecorator(Flag("raito__params", value=True))(kwargs)
