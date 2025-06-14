from __future__ import annotations

from asyncio import sleep
from pathlib import Path
from typing import TYPE_CHECKING, Union

from .base_router import BaseRouter
from .parser import RouterParser

if TYPE_CHECKING:
    from aiogram import Dispatcher, Router

PathOrStr = Union[Path, str]


class RouterLoader(BaseRouter, RouterParser):
    """A class for loading, unloading and reloading routers dynamically.

    :param name: Unique name of the router.
    :type name: str
    :param path: Path to the router file.
    :type path: str
    :param dispatcher: Aiogram dispatcher.
    :param router: Optional, pre-existing router instance, defaults to None
    :type router: Router, optional
    """

    def __init__(
        self,
        name: str,
        path: PathOrStr,
        dispatcher: Dispatcher,
        router: Router | None = None,
    ) -> None:
        """Initialize RouterLoader."""
        super().__init__(router)

        self.name = name
        self.path = Path(path)

        self._dispatcher = dispatcher

        self._router: Router | None = router
        self._parent_router: Router | None = None
        self._sub_routers: list[Router] = []

        self._is_restarting = False
        self._last_hash: str | None = None

    @property
    def router(self) -> Router:
        """Get or load the router instance."""
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
            self._dispatcher.include_router(router)

    def unload(self) -> None:
        """Unload and unregister the router."""
        if self.router:
            self._unlink_from_parent()
            self._router = None

    async def reload(self, timeout: float | None = None) -> None:
        """Reload the router with optional delay.

        :param timeout: Delay in seconds before reloading.
        """
        if not self._is_restarting:
            self._is_restarting = True
            self.unload()

            if timeout:
                await sleep(timeout)

            self.load()
            self._is_restarting = False
