import importlib.util
from asyncio import sleep
from pathlib import Path
from typing import TYPE_CHECKING

from aiogram import Router

if TYPE_CHECKING:
    from aiogram import Dispatcher


class RouterLoader:
    def __init__(
        self,
        name: str,
        path: str | Path,
        dispatcher: "Dispatcher",
        router: Router | None = None,
    ) -> None:
        self.name = name
        self.path = path
        self.dispatcher = dispatcher

        self._router: Router | None = router

        self._parent_router: Router | None = None
        self._sub_routers: list[Router] | None = None
        self._is_restarting: bool = False
        self._last_hash: str | None = None

    @classmethod
    def extract_router(cls, file_path: str | Path) -> "Router":
        module_spec = importlib.util.spec_from_file_location("dynamic_module", file_path)

        if module_spec is None or module_spec.loader is None:
            raise ModuleNotFoundError

        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        if not hasattr(module, "router") or not isinstance(module.router, Router):
            raise ModuleNotFoundError

        return module.router

    @property
    def router(self) -> Router | None:
        if self._router:
            return self._router

        try:
            self._router = self.extract_router(self.path)

            if self.name:
                self._router.name = self.name
        except ModuleNotFoundError:
            self._router = None

        return self._router

    def _link_parent_router(self, router: Router) -> None:
        if self._parent_router is not None:
            self._parent_router.sub_routers.append(router)

    def _link_subrouters(self, router: Router) -> None:
        if self._sub_routers is not None:
            for sub_router in self._sub_routers:
                sub_router._parent_router = router

    def load(self) -> None:
        if self.router is None:
            return

        self._link_parent_router(self.router)
        self._link_subrouters(self.router)

        self.dispatcher.include_router(self.router)

    def _unlink_from_parent(self, router: Router) -> None:
        if not router.parent_router:
            return

        for sub_router in router.parent_router.sub_routers:
            if sub_router.name == router.name:
                router.parent_router.sub_routers.remove(sub_router)

    def _unlink_sub_routers(self, router: Router) -> None:
        for sub_router in router.sub_routers:
            sub_router._parent_router = None

    def unload(self) -> None:
        if self.router is None:
            return

        self._parent_router = self.router.parent_router
        self._sub_routers = self.router.sub_routers

        self._unlink_from_parent(self.router)
        self._unlink_sub_routers(self.router)
        self._router = None

    async def reload(self, timeout: float | None = None) -> None:
        if self._is_restarting:
            return

        self._is_restarting = True
        self.unload()

        if timeout is not None:
            await sleep(timeout)

        self.load()
        self._is_restarting = False
