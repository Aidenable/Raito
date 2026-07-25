"""Tests for :class:`raito.core.routers.manager.RouterManager`."""

from __future__ import annotations

import logging

from raito.core.routers.loader import RouterLoader
from raito.core.routers.manager import RouterManager


def _write(directory, name: str, content: str):
    file_path = directory / name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return file_path


def test_resolve_paths_ignores_underscore_and_non_py(dispatcher, tmp_path):
    _write(tmp_path, "a.py", "from aiogram import Router\nrouter = Router(name='a')\n")
    _write(tmp_path, "_hidden.py", "from aiogram import Router\nrouter = Router(name='h')\n")
    _write(tmp_path, "readme.txt", "not python")
    _write(tmp_path, "pkg/b.py", "from aiogram import Router\nrouter = Router(name='b')\n")
    _write(tmp_path, "_pkg/c.py", "from aiogram import Router\nrouter = Router(name='c')\n")

    manager = RouterManager(dispatcher)

    resolved = {path.name for path in manager.resolve_paths(tmp_path)}

    assert resolved == {"a.py", "b.py"}


async def test_load_routers_respects_priority(dispatcher, tmp_path):
    _write(
        tmp_path,
        "low.py",
        "from raito import rt\nrouter = rt.Router(name='low', priority=1)\n",
    )
    _write(
        tmp_path,
        "high.py",
        "from raito import rt\nrouter = rt.Router(name='high', priority=10)\n",
    )

    manager = RouterManager(dispatcher)
    await manager.load_routers(tmp_path)

    names = [router.name for router in dispatcher.sub_routers]
    assert "high" in names
    assert "low" in names
    assert names.index("high") < names.index("low")


async def test_load_routers_resolves_name_conflict(dispatcher, tmp_path, caplog):
    _write(
        tmp_path,
        "first.py",
        "from raito import rt\nrouter = rt.Router(name='dup')\n",
    )
    _write(
        tmp_path,
        "second.py",
        "from raito import rt\nrouter = rt.Router(name='dup')\n",
    )

    manager = RouterManager(dispatcher)
    with caplog.at_level(logging.WARNING, logger="raito.core.routers"):
        await manager.load_routers(tmp_path)

    assert len(manager.loaders) == 2
    assert "dup" in manager.loaders
    renamed = [name for name in manager.loaders if name != "dup"]
    assert len(renamed) == 1
    assert renamed[0].startswith("dup_")

    loaded_names = {router.name for router in dispatcher.sub_routers}
    assert "dup" in loaded_names
    assert renamed[0] in loaded_names

    assert "Duplicate router name" in caplog.text


def test_create_loader_returns_loader_for_valid_file(dispatcher, tmp_path):
    file_path = _write(
        tmp_path,
        "valid.py",
        "from aiogram import Router\nrouter = Router(name='valid')\n",
    )

    manager = RouterManager(dispatcher)
    loader = manager._create_loader(file_path)

    assert isinstance(loader, RouterLoader)
    assert loader.name == "valid"
    assert manager.loaders["valid"] is loader


def test_create_loader_returns_none_for_non_router(dispatcher, tmp_path):
    file_path = _write(tmp_path, "invalid.py", "value = 1\n")

    manager = RouterManager(dispatcher)
    loader = manager._create_loader(file_path)

    assert loader is None
    assert manager.loaders == {}


def test_add_router_loads_new_file(dispatcher, tmp_path):
    file_path = _write(
        tmp_path,
        "new.py",
        "from aiogram import Router\nrouter = Router(name='new')\n",
    )

    manager = RouterManager(dispatcher)
    loader = manager._add_router(file_path)

    assert isinstance(loader, RouterLoader)
    assert loader.is_loaded is True
    assert "new" in {router.name for router in dispatcher.sub_routers}


def test_add_router_returns_none_for_non_router(dispatcher, tmp_path):
    file_path = _write(tmp_path, "junk.py", "value = 1\n")

    manager = RouterManager(dispatcher)
    loader = manager._add_router(file_path)

    assert loader is None
    assert dispatcher.sub_routers == []
