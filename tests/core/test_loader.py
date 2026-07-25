"""Tests for :class:`raito.core.routers.loader.RouterLoader`."""

from __future__ import annotations

import asyncio

from raito.core.routers.loader import RouterLoader
from raito.core.routers.parser import RouterParser


def _write_router(tmp_path, name: str = "r"):
    file_path = tmp_path / f"{name}.py"
    file_path.write_text(f"from aiogram import Router\nrouter = Router(name='{name}')\n")
    return file_path


def test_load_and_unload(dispatcher, tmp_path):
    file_path = _write_router(tmp_path)
    router = RouterParser.extract_router(file_path)
    loader = RouterLoader("r", file_path, dispatcher, router=router)

    assert loader.is_loaded is False
    assert loader.is_restarting is False

    loader.load()
    assert loader.is_loaded is True
    assert router in dispatcher.sub_routers

    loader.unload()
    assert loader.is_loaded is False
    assert router not in dispatcher.sub_routers


async def test_reload_reincludes_router(dispatcher, tmp_path):
    file_path = _write_router(tmp_path)
    router = RouterParser.extract_router(file_path)
    loader = RouterLoader("r", file_path, dispatcher, router=router)

    loader.load()
    assert loader.is_loaded is True

    await loader.reload()

    assert loader.is_loaded is True
    assert loader.is_restarting is False
    assert "r" in {sub.name for sub in dispatcher.sub_routers}


async def test_is_restarting_flag_during_reload(dispatcher, tmp_path):
    file_path = _write_router(tmp_path)
    router = RouterParser.extract_router(file_path)
    loader = RouterLoader("r", file_path, dispatcher, router=router)
    loader.load()

    assert loader.is_restarting is False

    task = asyncio.create_task(loader.reload(timeout=0.05))
    await asyncio.sleep(0.01)
    assert loader.is_restarting is True

    await task
    assert loader.is_restarting is False
    assert loader.is_loaded is True
