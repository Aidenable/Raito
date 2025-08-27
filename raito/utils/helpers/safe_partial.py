import inspect
from collections.abc import Callable
from functools import partial, update_wrapper
from typing import Any, ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")


def safe_partial(func: Callable[P, R], /, **kwargs: Any) -> Callable[P, R]:  # noqa: ANN401
    """
    Creates a partial version of a function, keeping only keyword arguments
    that are accepted by the original function.

    :param func: The original function to partially apply
    :param kwargs: Keyword arguments to bind
    :return: A new callable with partially applied arguments
    """
    signature = inspect.signature(func)

    valid_parameters = {
        name
        for name, param in signature.parameters.items()
        if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
    }

    filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_parameters}
    wrapped = partial(func, **filtered_kwargs)
    return cast(Callable[P, R], update_wrapper(wrapped, func))
