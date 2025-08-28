from collections.abc import Callable, Sequence
from functools import wraps
from typing import Literal, TypeAlias, cast, overload

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder,
)
from typing_extensions import ParamSpec, TypeVar

__all__ = ("static_keyboard",)


P = ParamSpec("P")
R = TypeVar("R")

ButtonData: TypeAlias = str | tuple[str] | tuple[str, str]
LayoutRow: TypeAlias = Sequence[ButtonData]
LayoutReturn: TypeAlias = Sequence[ButtonData | LayoutRow]

InlineSyncFn: TypeAlias = Callable[P, InlineKeyboardMarkup]
ReplySyncFn: TypeAlias = Callable[P, ReplyKeyboardMarkup]

KeyboardMarkupT: TypeAlias = InlineKeyboardMarkup | ReplyKeyboardMarkup
BuilderFn: TypeAlias = Callable[P, KeyboardMarkupT]


def _get_button(data: ButtonData, *, inline: bool) -> InlineKeyboardButton | KeyboardButton:
    """Convert button data to the appropriate button type.

    :param data: Button representation (e.g. :code:`("Text", "callback_data")`, or :code:`"Text"` for ReplyKeyboardMarkup)
    :param inline: Whether to create InlineKeyboardButton or KeyboardButton
    :return: An instance of aiogram button
    :raises ValueError: if inline button data is invalid
    """
    if not inline:
        return KeyboardButton(text=data if isinstance(data, str) else data[0])

    if isinstance(data, str) or len(data) != 2:
        raise ValueError("InlineKeyboardButton must be tuple of (text, callback_data)")
    return InlineKeyboardButton(text=data[0], callback_data=data[1])


def _is_button(row: LayoutRow) -> bool:
    """Determine whether a given layout row represents a single button.

    A row is considered a single button if:
    - It is a `str` (used as the text for a reply button), or
    - It is a `tuple[str]` or `tuple[str, str]` (used for inline buttons with callback data)

    :param row: A row from the layout, which may be a button or a list of buttons
    :return: True if the row is a single button, False if it is a row of buttons
    """
    if (
        isinstance(row, tuple | list)
        and 0 < len(row) <= 2
        and all(isinstance(item, str) for item in row)
    ):
        return True
    return isinstance(row, str)


def _inject_layout(
    builder: InlineKeyboardBuilder | ReplyKeyboardBuilder,
    layout: LayoutReturn,
    *,
    inline: bool,
) -> None:
    """Add declarative layout to the keyboard builder.

    :param builder: The builder instance
    :param layout: List of button data or rows
    :param inline: Whether inline buttons are expected
    """
    expected_type = InlineKeyboardBuilder if inline else ReplyKeyboardBuilder
    if not isinstance(builder, expected_type):
        kind = "Inline" if inline else "Reply"
        raise ValueError(f"{kind} buttons are not supported for {type(builder).__name__}")

    for row in layout:
        if _is_button(row):
            button = _get_button(cast(ButtonData, row), inline=inline)
            builder.row(button, width=1)  # type: ignore[arg-type]
        else:
            buttons = [_get_button(data, inline=inline) for data in row]
            builder.row(*buttons, width=min(8, len(row)))  # type: ignore[arg-type]


@overload
def static_keyboard(
    inline: Literal[True] = True, **builder_kwargs: object
) -> Callable[[Callable[P, LayoutReturn]], InlineSyncFn[P]]: ...
@overload
def static_keyboard(
    inline: Literal[False], **builder_kwargs: object
) -> Callable[[Callable[P, LayoutReturn]], ReplySyncFn[P]]: ...
def static_keyboard(
    inline: bool = True, **builder_kwargs: object
) -> Callable[[Callable[P, LayoutReturn]], BuilderFn[P]]:
    """Decorator to build inline or reply keyboards via layout style.

    Example:

    .. code-block:: python

        @keyboard(inline=True)
        def markup():
            return [
                ("Top Button", "top_callback_data"),
                [("Left", "left"), ("Right", "right")],
            ]

    :param inline: If True, builds InlineKeyboardMarkup
    :param builder_kwargs: Extra args passed to `as_markup()`
    :returns: A wrapped function returning KeyboardMarkup
    """
    if not inline:
        builder_kwargs.setdefault("resize_keyboard", True)

    Builder = InlineKeyboardBuilder if inline else ReplyKeyboardBuilder

    def wrapper(fn: Callable[P, LayoutReturn]) -> BuilderFn[P]:
        @wraps(fn)
        def sync_fn(*args: P.args, **kwargs: P.kwargs) -> KeyboardMarkupT:
            value = fn(*args, **kwargs)

            if not isinstance(value, list):
                msg = "Function must return a list"
                raise ValueError(msg)

            builder = Builder()
            _inject_layout(builder, value, inline=inline)
            return builder.as_markup(**builder_kwargs)

        return sync_fn

    return wrapper
