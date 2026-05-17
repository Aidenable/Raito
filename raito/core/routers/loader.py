from __future__ import annotations

from asyncio import sleep
from pathlib import Path
from typing import TYPE_CHECKING

from .base_router import BaseRouter
from .parser import RouterParser
from .router import Router as RaitoRouter

if TYPE_CHECKING:
    from aiogram import Dispatcher, Router

    from raito.utils.types import StrOrPath


__all__ = ("RouterLoader",)


class RouterLoader(BaseRouter, RouterParser):
    """A class for loading, unloading and reloading routers dynamically."""

    def __init__(
        self,
        name: str,
        path: StrOrPath,
        dispatcher: Dispatcher,
        router: Router | None = None,
    ) -> None:
        """Initialize RouterLoader.

        :param name: Unique name of the router
        :type name: str
        :param path: Path to the router file
        :type path: StrOrPath
        :param dispatcher: Aiogram dispatcher
        :type dispatcher: Dispatcher
        :param router: Router (aiogram or Raito) instance, defaults to None
        :type router: aiogram.Router | raito.Router | None, optional
        """
        super().__init__(router)

        self.name = name
        self.path = Path(path)

        self._dispatcher = dispatcher

        self._router: Router | None = router
        self._parent_router: Router | None = router.parent_router if router else None
        self._sub_routers: list[Router] = router.sub_routers if router else []

        self._is_restarting: bool = False
        self._is_loaded: bool = False
        self._saved_index: int | None = None

    @property
    def priority(self) -> int:
        """Get router loading priority

        :return: Integer from -inf to +inf
        :rtype: int
        """
        if isinstance(self._router, RaitoRouter):
            return self._router.priority
        return 0

    @property
    def autoload(self) -> bool:
        """Should router autoload

        :return: True if autload is turned on, otherwise False
        :rtype: bool
        """
        if isinstance(self._router, RaitoRouter):
            return self._router.autoload
        return True

    @property
    def is_loaded(self) -> bool:
        """Check whether the router is currently loaded.

        :return: True if the router has been loaded and registered into the dispatcher
        :rtype: bool
        """
        return self._is_loaded

    @property
    def is_restarting(self) -> bool:
        """Check whether the router is currently being reloaded.

        :return: True if a reload operation is in progress
        :rtype: bool
        """
        return self._is_restarting

    @property
    def router(self) -> Router:
        """Get or load the router instance.

        :return: The router instance
        :rtype: aiogram.Router | raito.Router
        """
        if self._router is None:
            self._router = self.extract_router(self.path)
            if not hasattr(self._router, "name"):
                self._router.name = self.name
        return self._router

    def load(self) -> None:
        """Load and register the router."""
        if router := self.router:
            if self._parent_router:
                self._link_to_parent(self._parent_router)

            if self._saved_index is not None:
                self._dispatcher.sub_routers.insert(self._saved_index, router)
                self._saved_index = None
            else:
                self._dispatcher.include_router(router)

        self._is_loaded = True

    def unload(self) -> None:
        """Unload and unregister the router."""
        if self.router:
            try:
                self._saved_index = self._dispatcher.sub_routers.index(self.router)
            except ValueError:
                self._saved_index = None

            if self.router in self._dispatcher.sub_routers:
                self._dispatcher.sub_routers.remove(self.router)

            self._unlink_from_parent()
            self._router = None

        self._is_loaded = False

    async def reload(self, timeout: float | None = None) -> None:
        """Reload the router with optional delay.

        :param timeout: Delay in seconds before reloading, defaults to None
        :type timeout: float | None, optional
        """
        if not self._is_restarting:
            self._is_restarting = True
            self.unload()

            if timeout:
                await sleep(timeout)

            self.load()
            self._is_restarting = False
