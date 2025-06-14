from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Union

from aiogram import Router

PathOrStr = Union["Path", str]


class RouterParser:
    """Parses routers from Python files."""

    @classmethod
    def extract_router(cls, file_path: PathOrStr) -> Router:
        """Extract router from a Python file.

        :param file_path: Path to the Python File.
        :return: Extracted router instance.
        """
        file_path = Path(file_path)
        module = cls._load_module(file_path)
        return cls._validate_router(module)

    @classmethod
    def _load_module(cls, file_path: Path) -> object:
        """Load module from file path."""
        spec = spec_from_file_location("dynamic_module", file_path)

        if spec is None or spec.loader is None:
            msg = f"Cannot load module from {file_path}"
            raise ModuleNotFoundError(msg)

        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @classmethod
    def _validate_router(cls, module: object) -> Router:
        """Validate and return router from module."""
        if not hasattr(module, "router"):
            msg = "Module missing 'router' attribute."

        router = module.router
        if not isinstance(router, Router):
            msg = f"Excepted Router, got {type(router).__name__}"
            raise TypeError(msg)

        return router
