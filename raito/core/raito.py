from __future__ import annotations

import logging
import sys
from asyncio import create_task
from typing import TYPE_CHECKING

from aiogram.dispatcher.event.event import EventObserver
from aiogram.dispatcher.event.handler import CallbackType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from raito.plugins.album.middleware import AlbumMiddleware
from raito.plugins.commands.middleware import CommandMiddleware
from raito.plugins.commands.registration import register_bot_commands
from raito.plugins.conversations import (
    ConversationMiddleware,
    ConversationRegistry,
    Waiter,
    wait_for,
)
from raito.plugins.pagination import PaginationMode, PaginatorMiddleware, get_paginator
from raito.plugins.roles import (
    BaseRoleProvider,
    IRoleProvider,
    MemoryRoleProvider,
    RoleManager,
)
from raito.plugins.roles.providers import (
    get_postgresql_provider,
    get_redis_provider,
    get_sqlite_provider,
)
from raito.plugins.roles.providers.json import JSONRoleProvider
from raito.plugins.throttling.middleware import THROTTLING_MODE, ThrottlingMiddleware
from raito.utils import loggers
from raito.utils.configuration import RaitoConfiguration
from raito.utils.const import ROOT_DIR
from raito.utils.storages import (
    get_postgresql_storage,
    get_redis_storage,
    get_sqlite_storage,
)
from raito.utils.storages.json import JSONStorage

from .routers.manager import RouterManager

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.base import BaseStorage
    from aiogram.types import Message, User

    from raito.plugins.roles import IRoleProvider
    from raito.utils.types import StrOrPath

__all__ = ("Raito",)


class Raito:
    """Main class for managing the Raito utilities.

    Provides router management, middleware setup, etc.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        routers_dir: StrOrPath,
        *,
        developers: list[int] | None = None,
        locales: list[str] | None = None,
        production: bool = True,
        configuration: RaitoConfiguration | None = None,
        storage: BaseStorage | None = None,
    ) -> None:
        """Initialize the Raito.

        :param dispatcher: Aiogram dispatcher instance
        :type dispatcher: Dispatcher
        :param routers_dir: Directory containing router files
        :type routers_dir: StrOrPath
        :param developers: List of developer user IDs with special privileges, defaults to None
        :type developers: list[int] | None, optional
        :param locales: List of supported locales (e.g., "en", "ru")
        :type locales: list[str]
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
        self.locales = locales or []
        self.production = production
        self.configuration = configuration or RaitoConfiguration()
        self.storage = storage or MemoryStorage()

        self.router_manager = RouterManager(dispatcher)
        self.dispatcher["raito"] = self

        self._role_provider = self._get_role_provider(self.storage)
        self.role_manager = self.configuration.role_manager or RoleManager(
            self._role_provider, developers=self.developers
        )

        self.command_parameters_error = EventObserver()
        self.registry = ConversationRegistry()

    async def setup(self) -> None:
        """Set up the Raito by loading routers and starting watchdog.

        Loads all routers from the specified directory and starts file watching
        in development mode for automatic reloading.
        """
        loggers.core.info(
            "[ 🔦 Raito ] Running in %s mode",
            "production" if self.production else "development",
        )

        provider = self.role_manager.provider
        if self.production and isinstance(provider, (MemoryRoleProvider | JSONRoleProvider)):
            loggers.roles.warn(
                "Using %s. It's not recommended for production use.",
                provider.__class__.__name__,
            )
        await self.role_manager.migrate()

        self.dispatcher.callback_query.middleware(PaginatorMiddleware("raito__is_pagination"))
        self.dispatcher.message.middleware(CommandMiddleware())
        self.dispatcher.message.middleware(AlbumMiddleware())
        self.dispatcher.message.outer_middleware(ConversationMiddleware(self.registry))

        await self.router_manager.load_routers(self.routers_dir)
        await self.router_manager.load_routers(ROOT_DIR / "handlers")

        if not self.production:
            create_task(self.router_manager.start_watchdog(self.routers_dir))  # noqa: RUF006

    def add_throttling(
        self,
        rate_limit: float,
        mode: THROTTLING_MODE = "chat",
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
        middleware = ThrottlingMiddleware(rate_limit=rate_limit, mode=mode, max_size=max_size)
        self.dispatcher.callback_query.middleware(middleware)
        self.dispatcher.message.middleware(middleware)

    def _get_role_provider(self, storage: BaseStorage) -> IRoleProvider:
        """Get the current role provider based on storage.

        :return: Role provider instance
        :rtype: IRoleProvider
        """
        if isinstance(storage, MemoryStorage):
            return MemoryRoleProvider(storage)

        if isinstance(storage, JSONStorage):
            return JSONRoleProvider(storage)

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

    async def paginate(
        self,
        name: str,
        chat_id: int,
        bot: Bot,
        from_user: User,
        *,
        existing_message: Message | None = None,
        mode: PaginationMode = PaginationMode.INLINE,
        current_page: int = 1,
        total_pages: int | None = None,
        limit: int = 20,
    ) -> None:
        Paginator = get_paginator(mode)
        paginator = Paginator(
            raito=self,
            name=name,
            chat_id=chat_id,
            bot=bot,
            from_user=from_user,
            existing_message=existing_message,
            current_page=current_page,
            total_pages=total_pages,
            limit=limit,
        )
        await paginator.paginate()

    async def register_commands(self, bot: Bot) -> None:
        handlers = []
        for loader in self.router_manager.loaders.values():
            handlers.extend(loader.router.message.handlers)

        await register_bot_commands(
            role_manager=self.role_manager,
            bot=bot,
            handlers=handlers,
            locales=self.locales,
        )

    def init_logging(self, *mute_loggers: str) -> None:
        """Configure global logging with a colored formatter.

        :param mute_loggers: List of logger names to suppress from output
        """
        logging.captureWarnings(True)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(loggers.ColoredFormatter())
        if mute_loggers:
            handler.addFilter(loggers.MuteLoggersFilter(*mute_loggers))

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG if not self.production else logging.INFO)

    async def wait_for(self, context: FSMContext, *filters: CallbackType) -> Waiter:
        """Wait for the next message from user that matches given filters.

        This function sets special state ``raito__conversation`` in FSM and
        suspends coroutine execution until user sends a message that passes
        all provided filters. Result is wrapped into :class:`Waiter`.

        :param context: FSM context for current chat
        :param filters: Sequence of aiogram filters
        :return: Conversation result with text, parsed number and original message
        :raises RuntimeError: If handler object not found during filter execution
        :raises asyncio.CancelledError: If conversation was cancelled
        """
        return await wait_for(self, context, *filters)
