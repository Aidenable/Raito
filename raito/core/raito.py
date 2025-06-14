from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from aiogram import Dispatcher

from raito.utils.middlewares import ThrottlingMiddleware

from .routers.manager import RoutersManager

if TYPE_CHECKING:
    from aioredis import Redis
    from pydantic import PostgresDsn


class Raito:
    def __init__(
        self,
        dispatcher: "Dispatcher",
        routers_dir: str | Path,
        developers: list[int],
        database: Union["PostgresDsn", str],
        production: bool = True,
        redis: Optional["Redis"] = None,
    ):
        self.dispatcher = dispatcher
        self.routers_dir = routers_dir
        self.developers = developers
        self.database = database
        self.production = production
        self.redis = redis

        self.manager = RoutersManager(dispatcher, watchdog=not production)

    async def setup(self) -> None:
        await self.manager.load_routers(self.routers_dir)

    async def add_global_throttling(
        self,
        rate_limit: float,
        mode: ThrottlingMiddleware.MODE = "chat",
        max_size: int = 10_000,
    ) -> None:
        self.dispatcher.callback_query.outer_middleware(
            ThrottlingMiddleware(rate_limit=rate_limit, mode=mode, max_size=max_size)
        )
        self.dispatcher.message.outer_middleware(
            ThrottlingMiddleware(rate_limit=rate_limit, mode=mode, max_size=max_size)
        )
