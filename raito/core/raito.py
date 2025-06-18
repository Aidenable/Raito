from asyncio import create_task
from typing import TYPE_CHECKING, Optional, Union

from raito.plugins.roles.manager import RoleManager
from raito.plugins.roles.providers.memory import MemoryRoleProvider
from raito.utils.configuration import Configuration
from raito.utils.const import ROOT_DIR
from raito.utils.middlewares import ThrottlingMiddleware

from .routers.manager import RouterManager

if TYPE_CHECKING:
    from aiogram import Dispatcher
    from aioredis import Redis
    from pydantic import PostgresDsn

    from raito.utils.types import StrOrPath


class Raito:
    """Main class for managing the Raito utilities.

    Provides router management, middleware setup, etc.
    """

    def __init__(
        self,
        dispatcher: "Dispatcher",
        routers_dir: "StrOrPath",
        developers: list[int],
        database: Union["PostgresDsn", str],
        *,
        production: bool = True,
        configuration: Configuration | None = None,
        redis: Optional["Redis"] = None,
    ) -> None:
        """Initialize the Raito.

        :param dispatcher: Aiogram dispatcher instance
        :type dispatcher: Dispatcher
        :param routers_dir: Directory containing router files
        :type routers_dir: StrOrPath
        :param developers: List of developer user IDs with special privileges
        :type developers: list[int]
        :param database: Database connection string
        :type database: PostgresDsn | str
        :param production: Whether running in production mode, defaults to True
        :type production: bool, optional
        :param redis: Redis connection instance for caching, defaults to None
        :type redis: Redis | None, optional
        """
        self.dispatcher = dispatcher
        self.routers_dir = routers_dir
        self.developers = developers
        self.database = database
        self.production = production
        self.configuration = configuration or Configuration()
        self.redis = redis

        self.router_manager = RouterManager(dispatcher)
        self.dispatcher["raito"] = self

        self._role_provider = MemoryRoleProvider()
        self.role_manager = RoleManager(self._role_provider, developers=self.developers)

    async def setup(self) -> None:
        """Set up the Raito by loading routers and starting watchdog.

        Loads all routers from the specified directory and starts file watching
        in development mode for automatic reloading.
        """
        await self.role_manager.initialize(self.dispatcher)

        await self.router_manager.load_routers(self.routers_dir)
        await self.router_manager.load_routers(ROOT_DIR / "handlers")

        if not self.production:
            create_task(self.router_manager.start_watchdog(self.routers_dir))  # noqa: RUF006

    def add_global_throttling(
        self,
        rate_limit: float,
        mode: ThrottlingMiddleware.MODE = "chat",
        max_size: int = 10_000,
    ) -> None:
        """Add global throttling middleware to prevent spam.

        Applies rate limiting to both messages and callback queries.

        :param rate_limit: Time in seconds between allowed requests
        :type rate_limit: float
        :param mode: Throttling mode - 'chat', 'user', or 'bot', defaults to 'chat'
        :type mode: ThrottlingMiddleware.MODE, optional
        :param max_size: Maximum cache size for throttling records, defaults to 10_000
        :type max_size: int, optional
        """
        self.dispatcher.callback_query.outer_middleware(
            ThrottlingMiddleware(rate_limit=rate_limit, mode=mode, max_size=max_size),
        )
        self.dispatcher.message.outer_middleware(
            ThrottlingMiddleware(rate_limit=rate_limit, mode=mode, max_size=max_size),
        )
