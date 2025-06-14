import asyncio
from collections.abc import Generator
from os import listdir, path
from pathlib import Path
from typing import TYPE_CHECKING

from raito.utils import loggers

from .loader import RouterLoader

if TYPE_CHECKING:
    from aiogram import Dispatcher


class RoutersManager:
    def __init__(
        self,
        dispatcher: "Dispatcher",
        watchdog: bool = False,
        *,
        watchdog_interval: float = 1.0,
    ) -> None:
        self.dispatcher = dispatcher
        self.watchdog = watchdog
        self.watchdog_interval = watchdog_interval

        self._routers: dict[str, RouterLoader] = {}
        self._watchdogs: list[asyncio.Task[None]] = []

    def resolve_paths(self, directory: str | Path) -> Generator[Path | str, None, None]:
        for file_name in listdir(directory):
            file_path = Path(directory, file_name)

            if file_name.startswith("_"):  # ignore files with prefix _
                continue

            if path.isfile(file_path) and file_name.endswith(".py"):
                yield file_path
            elif path.isdir(file_path):
                yield from self.resolve_paths(file_path)

    async def load_routers(self, directory: str | Path) -> None:
        names = set()

        for file_path in self.resolve_paths(directory):
            try:
                router = RouterLoader.extract_router(file_path)
            except ModuleNotFoundError:
                loggers.core.error("Module not found: %s", file_path)
                continue

            unique_name: str = router.name
            if router.name in names:
                suffix = hex(id(router))
                unique_name = f"{router.name}_{suffix}"

                loggers.core.warning(
                    "Duplicate router name: %s. Will rename to %s...",
                    router.name,
                    unique_name,
                )
                router.name = unique_name
            names.add(router.name)

            loader = RouterLoader(
                unique_name,
                file_path,
                self.dispatcher,
                router=router,
            )
            loader.load()
            self._routers[unique_name] = loader
            loggers.core.info("Router loaded: %s", unique_name)

            if self.watchdog:
                task = asyncio.create_task(loader.watchdog(interval=self.watchdog_interval))
                self._watchdogs.append(task)
