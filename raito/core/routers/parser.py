from __future__ import annotations

import sys
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
        module_name = f"_raito_router_{Path(file_path).stem}_{abs(hash(str(file_path)))}"
        spec = spec_from_file_location(module_name, file_path)

        if spec is None or spec.loader is None:
            msg = f"Cannot load module from {file_path}"
            raise ModuleNotFoundError(msg)

        module = module_from_spec(spec)
        module.__name__ = spec.name
        module.__file__ = str(file_path)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        return module

    @classmethod
    def _validate_router(cls, module: object) -> Router:
        """Validate and return a router from the module.

        Prefers a module-level variable named ``router``. Otherwise, looks the
        module up by type for a single :class:`aiogram.Router` (or
        :class:`raito.Router`) instance regardless of its variable name.

        :param module: Module object to extract router from
        :type module: object
        :return: Validated router instance
        :rtype: Router
        :raises TypeError: If the module contains no router, or more than one
            and none of them is named ``router``
        """
        router = getattr(module, "router", None)
        if isinstance(router, Router):
            return router

        routers = {name: value for name, value in vars(module).items() if isinstance(value, Router)}
        unique = {id(value): value for value in routers.values()}

        if len(unique) == 1:
            return next(iter(unique.values()))

        if not unique:
            msg = "Expected a Router instance (named `router` or found by type), but got none"
            raise TypeError(msg)

        names = ", ".join(sorted(routers))
        msg = f"Found multiple routers ({names}); name one of them `router` to avoid conflicts"
        raise TypeError(msg)
