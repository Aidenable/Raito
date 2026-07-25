"""Tests for :class:`raito.core.routers.parser.RouterParser`."""

from __future__ import annotations

import pytest
from aiogram import Router

from raito.core.routers.parser import RouterParser


def _write(tmp_path, name: str, content: str):
    file_path = tmp_path / name
    file_path.write_text(content)
    return file_path


def test_extract_router_named_router(tmp_path):
    file_path = _write(
        tmp_path,
        "named.py",
        "from aiogram import Router\nrouter = Router(name='x')\n",
    )

    router = RouterParser.extract_router(file_path)

    assert isinstance(router, Router)
    assert router.name == "x"


def test_extract_router_other_variable_name(tmp_path):
    file_path = _write(
        tmp_path,
        "other.py",
        "from aiogram import Router\nmy_router = Router(name='y')\n",
    )

    router = RouterParser.extract_router(file_path)

    assert isinstance(router, Router)
    assert router.name == "y"


def test_extract_router_raito_rt_by_type(tmp_path):
    file_path = _write(
        tmp_path,
        "rt_router.py",
        "from raito import rt\nhandler = rt.Router(name='z')\n",
    )

    router = RouterParser.extract_router(file_path)

    assert isinstance(router, Router)
    assert router.name == "z"


def test_extract_router_multiple_without_named_router(tmp_path):
    file_path = _write(
        tmp_path,
        "multiple.py",
        "from aiogram import Router\na = Router(name='a')\nb = Router(name='b')\n",
    )

    with pytest.raises(TypeError):
        RouterParser.extract_router(file_path)


def test_extract_router_same_router_two_aliases(tmp_path):
    file_path = _write(
        tmp_path,
        "aliases.py",
        "from aiogram import Router\nmain = Router(name='m')\nalias = main\n",
    )

    router = RouterParser.extract_router(file_path)

    assert isinstance(router, Router)
    assert router.name == "m"


def test_extract_router_no_router(tmp_path):
    file_path = _write(
        tmp_path,
        "empty.py",
        "value = 123\n",
    )

    with pytest.raises(TypeError):
        RouterParser.extract_router(file_path)
