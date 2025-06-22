from asyncio import create_task
from typing import TYPE_CHECKING

from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage

from raito.plugins.roles import (
    BaseRoleProvider,
    IRoleProvider,
    MemoryRoleProvider,
    RoleManager,
)
from raito.plugins.roles.providers import get_redis_provider
from raito.plugins.roles.providers.sql import (
    get_postgresql_provider,
    get_sqlite_provider,
)
from raito.utils import loggers
from raito.utils.configuration import Configuration
from raito.utils.const import ROOT_DIR
from raito.utils.middlewares import ThrottlingMiddleware
from raito.utils.storages import (
    get_postgresql_storage,
    get_sqlite_storage,
)
from raito.utils.storages.sql import get_redis_storage

from .routers.manager import RouterManager

if TYPE_CHECKING:
    from aiogram import Dispatcher

    from raito.utils.types import StrOrPath

__all__ = ("Raito",)


class Raito:
    """Main class for managing the Raito utilities.

    Provides router management, middleware setup, etc.
    """

    def __init__(
        self,
        dispatcher: "Dispatcher",
        routers_dir: "StrOrPath",
        *,
        developers: list[int] | None = None,
        production: bool = True,
        configuration: Configuration | None = None,
        storage: BaseStorage | None = None,
    ) -> None:
        """Initialize the Raito.

        :param dispatcher: Aiogram dispatcher instance
        :type dispatcher: Dispatcher
        :param routers_dir: Directory containing router files
        :type routers_dir: StrOrPath
        :param developers: List of developer user IDs with special privileges, defaults to None
        :type developers: list[int] | None, optional
        :param production: Whether running in production mode, defaults to True
        :type production: bool, optional
        :param configuration: Configuration instance, defaults to Configuration()
        :type configuration: Configuration | None, optional
        :param storage: Aiogram storage instance for storing data, default None
        :type storage: BaseStorage | None, optional
        """
        self.dispatcher = dispatcher
        self.routers_dir = routers_dir
        self.developers = developers or []
        self.production = production
        self.configuration = configuration or Configuration()
        self.storage = storage or MemoryStorage()

        self.router_manager = RouterManager(dispatcher)
        self.dispatcher["raito"] = self

        self._role_provider = self.configuration.role_provider or self._get_role_provider(
            self.storage,
        )
        self.role_manager = RoleManager(self._role_provider, developers=self.developers)

    async def setup(self) -> None:
        """Set up the Raito by loading routers and starting watchdog.

        Loads all routers from the specified directory and starts file watching
        in development mode for automatic reloading.
        """
        loggers.core.info(
            "[ 🔦 Raito ] Running in %s mode",
            "production" if self.production else "development",
        )

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

    def _get_role_provider(self, storage: BaseStorage) -> "IRoleProvider":
        """Get the current role provider based on storage.

        :return: Role provider instance
        :rtype: IRoleProvider
        """
        if isinstance(storage, MemoryStorage):
            return MemoryRoleProvider(storage)

        redis_storage = get_redis_storage(throw=False)
        if redis_storage is not None and isinstance(storage, redis_storage):
            return get_redis_provider()(storage)

        postgresql_storage = get_postgresql_storage(throw=False)
        if postgresql_storage is not None and isinstance(storage, postgresql_storage):
            return get_postgresql_provider()(storage)

        sqlite_storage = get_sqlite_storage(throw=False)
        if sqlite_storage is not None and isinstance(storage, sqlite_storage):
            return get_sqlite_provider()(storage)

        return BaseRoleProvider(storage)
