from collections.abc import Callable
from functools import wraps
from typing import Literal, TypeAlias, overload

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    KeyboardBuilder,
    ReplyKeyboardBuilder,
)

from raito.utils.helpers.safe_partial import safe_partial

__all__ = ("keyboard",)


ButtonData: TypeAlias = str | tuple[str] | tuple[str, str] | list[str]

InlineSyncFn: TypeAlias = Callable[..., InlineKeyboardMarkup]
ReplySyncFn: TypeAlias = Callable[..., ReplyKeyboardMarkup]

KeyboardMarkupT: TypeAlias = InlineKeyboardMarkup | ReplyKeyboardMarkup
BuilderFn: TypeAlias = Callable[..., KeyboardMarkupT]


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


def _inject_layout(
    builder: KeyboardBuilder,
    layout: list[list[ButtonData] | ButtonData],
    *,
    inline: bool,
) -> None:
    """Add declarative layout to the keyboard builder.

    :param builder: The builder instance
    :param layout: List of button data or rows
    :param inline: Whether inline buttons are expected
    """
    for row in layout:
        if isinstance(row, list):
            buttons = [_get_button(data, inline=inline) for data in row]
            width = len(row)
        else:
            buttons = [_get_button(row, inline=inline)]
            width = 1

        builder.row(*buttons, width=width)


@overload
def keyboard(
    *sizes: int,
    repeat: bool = True,
    adjust: bool = True,
    inline: Literal[True] = True,
    **builder_kwargs: object,
) -> Callable[[Callable[..., object]], InlineSyncFn]: ...
@overload
def keyboard(
    *sizes: int,
    repeat: bool = True,
    adjust: bool = True,
    inline: Literal[False],
    **builder_kwargs: object,
) -> Callable[[Callable[..., object]], ReplySyncFn]: ...
def keyboard(
    *sizes: int,
    repeat: bool = True,
    adjust: bool = True,
    inline: bool = True,
    **builder_kwargs: object,
) -> Callable[..., BuilderFn]:
    """
    Decorator to build inline or reply keyboards via builder or layout style.

    Supports two styles:

    1. Builder pattern (recommended for dynamic keyboards):

       .. code-block:: python

          @keyboard(inline=True)
          def markup(builder: InlineKeyboardBuilder, name: str | None = None):
              if name is not None:
                builder.button(text=f"Hello, {name}", callback_data="hello")
              builder.button(text="Back", callback_data="back")

    2. Declarative layout (recommended for static keyboards):

       .. code-block:: python

          @keyboard(inline=True)
          def markup():
              return [
                  ("Top Button", "top"),
                  [("Left", "left"), ("Right", "right")],
              ]

    :param sizes: Row sizes passed to `adjust(...)`
    :param repeat: Whether adjust sizes should repeat
    :param adjust: Auto-adjust layout if True
    :param inline: If True, builds InlineKeyboardMarkup
    :param builder_kwargs: Extra args passed to `as_markup()`
    :returns: A wrapped function returning KeyboardMarkup
    """
    if not sizes:
        sizes = (1,)

    Builder = InlineKeyboardBuilder if inline else ReplyKeyboardBuilder

    def _build_markup(builder: KeyboardBuilder, *, adjust: bool) -> KeyboardMarkupT:
        if adjust:
            builder.adjust(*sizes, repeat=repeat)
        return builder.as_markup(**builder_kwargs)

    def wrapper(fn: Callable[..., object]) -> BuilderFn:
        @wraps(fn)
        def sync_fn(*args: object, **kwargs: object) -> KeyboardMarkupT:
            builder = Builder()
            result = safe_partial(fn, builder=builder)(*args, **kwargs)

            if isinstance(result, list):
                _inject_layout(builder, result, inline=inline)
                return _build_markup(builder, adjust=False)

            return _build_markup(builder, adjust=adjust)

        return sync_fn

    return wrapper
