from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import TYPE_CHECKING

from aiogram import Router

if TYPE_CHECKING:
    from raito.utils.types import StrOrPath


__all__ = ("RouterParser",)


class RouterParser:
    """Parses routers from Python files."""

    @classmethod
    def extract_router(cls, file_path: StrOrPath) -> Router:
        """Extract router from a Python file.

        :param file_path: Path to the Python file
        :type file_path: StrOrPath
        :return: Extracted router instance
        :rtype: Router
        """
        file_path = Path(file_path)
        module = cls._load_module(file_path)
        return cls._validate_router(module)

    @classmethod
    def _load_module(cls, file_path: StrOrPath) -> object:
        """Load module from file path.

        :param file_path: Path to the Python file to load
        :type file_path: StrOrPath
        :return: Loaded module object
        :rtype: object
        :raises ModuleNotFoundError: If module cannot be loaded from the file path
        """
        spec = spec_from_file_location("dynamic_module", file_path)

        if spec is None or spec.loader is None:
            msg = f"Cannot load module from {file_path}"
            raise ModuleNotFoundError(msg)

        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @classmethod
    def _validate_router(cls, module: object) -> Router:
        """Validate and return router from module.

        :param module: Module object to extract router from
        :type module: object
        :return: Validated router instance
        :rtype: Router
        :raises TypeError: If the module doesn't contain a valid Router instance
        """
        router = getattr(module, "router", None)
        if not isinstance(router, Router):
            msg = f"Expected Router, got {type(router).__name__}"
            raise TypeError(msg)

        return router
