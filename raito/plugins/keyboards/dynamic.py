from collections.abc import Callable
from functools import wraps
from typing import Concatenate, Literal, TypeAlias, cast, overload

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing_extensions import ParamSpec, TypeVar

__all__ = ("dynamic_keyboard",)


P = ParamSpec("P")
BuilderT = TypeVar("BuilderT", InlineKeyboardBuilder, ReplyKeyboardBuilder)

ButtonData: TypeAlias = str | tuple[str] | tuple[str, str] | list[str]
KeyboardMarkupT: TypeAlias = InlineKeyboardMarkup | ReplyKeyboardMarkup

InlineFn: TypeAlias = Callable[Concatenate[InlineKeyboardBuilder, P], object]
ReplyFn: TypeAlias = Callable[Concatenate[ReplyKeyboardBuilder, P], object]

InlineSyncFn: TypeAlias = Callable[P, InlineKeyboardMarkup]
ReplySyncFn: TypeAlias = Callable[P, ReplyKeyboardMarkup]


@overload
def dynamic_keyboard(
    *sizes: int,
    repeat: bool = True,
    adjust: bool = True,
    inline: Literal[True] = True,
    **builder_kwargs: object,
) -> Callable[[InlineFn[P]], InlineSyncFn[P]]: ...
@overload
def dynamic_keyboard(
    *sizes: int,
    repeat: bool = True,
    adjust: bool = True,
    inline: Literal[False],
    **builder_kwargs: object,
) -> Callable[[ReplyFn[P]], ReplySyncFn[P]]: ...
def dynamic_keyboard(  # type: ignore[misc]
    *sizes: int,
    repeat: bool = True,
    adjust: bool = True,
    inline: bool = True,
    **builder_kwargs: object,
) -> Callable[[Callable[Concatenate[BuilderT, P], object]], Callable[P, KeyboardMarkupT]]:
    """Decorator to build inline or reply keyboards via builder style.

    Example:

       .. code-block:: python

          @keyboard(inline=True)
          def markup(builder: InlineKeyboardBuilder, name: str | None = None):
              if name is not None:
                builder.button(text=f"Hello, {name}", callback_data="hello")
              builder.button(text="Back", callback_data="back")

    :param sizes: Row sizes passed to `adjust(...)`
    :param repeat: Whether adjust sizes should repeat
    :param adjust: Auto-adjust layout if True
    :param inline: If True, builds InlineKeyboardMarkup
    :param builder_kwargs: Extra args passed to `as_markup()`
    :returns: A wrapped function returning KeyboardMarkup
    """
    if not sizes:
        sizes = (1,)

    if not inline:
        builder_kwargs.setdefault("resize_keyboard", True)

    Builder = InlineKeyboardBuilder if inline else ReplyKeyboardBuilder

    def wrapper(fn: Callable[Concatenate[BuilderT, P], object]) -> Callable[P, KeyboardMarkupT]:
        @wraps(fn)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> KeyboardMarkupT:
            builder = Builder()
            fn(cast(BuilderT, builder), *args, **kwargs)
            if adjust:
                builder.adjust(*sizes, repeat=repeat)
            return builder.as_markup(**builder_kwargs)

        return wrapped

    return wrapper
