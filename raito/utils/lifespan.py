from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager, suppress
from typing import TypeAlias

from aiogram import Bot, Router

from raito.utils.helpers.safe_partial import safe_partial

__all__ = ("lifespan",)

FuncType: TypeAlias = Callable[..., AsyncGenerator[None, None]]
AsyncCtx: TypeAlias = AbstractAsyncContextManager[None]
LifespanStacks: TypeAlias = dict[int, list[AsyncCtx]]

_LIFESPAN_STACKS = "__lifespan_stacks__"


def _get_stack(router: Router) -> LifespanStacks:
    stacks = getattr(router, _LIFESPAN_STACKS, None)
    if stacks is None:
        stacks = {}
        setattr(router, _LIFESPAN_STACKS, stacks)
    return stacks


def lifespan(router: Router) -> Callable[[FuncType], FuncType]:
    """
    Register a lifespan function for a given router, similar to FastAPI's lifespan handler.
    The function must be an async generator: it runs setup before `yield`, and cleanup after.
    """

    def decorator(func: FuncType) -> FuncType:
        @asynccontextmanager
        async def context(**kwargs: dict[str, object]) -> AsyncGenerator[None, None]:
            gen = safe_partial(func, **kwargs)()
            await gen.__anext__()
            try:
                yield
            finally:
                with suppress(StopAsyncIteration):
                    await gen.__anext__()

        async def on_startup(**kwargs: dict[str, object]) -> None:
            bot = kwargs.get("bot")
            assert isinstance(bot, Bot), "Missing or invalid 'bot' in lifespan context"

            ctx = context(**kwargs)
            await ctx.__aenter__()
            _get_stack(router).setdefault(bot.id, []).append(ctx)

        async def on_shutdown(**kwargs: dict[str, object]) -> None:
            bot = kwargs.get("bot")
            assert isinstance(bot, Bot), "Missing or invalid 'bot' in lifespan context"

            stack = _get_stack(router).get(bot.id, [])
            for ctx in reversed(stack):
                await ctx.__aexit__(None, None, None)
            stack.clear()

        router.startup.register(on_startup)
        router.shutdown.register(on_shutdown)

        return func

    return decorator
