"""Tests for raito.plugins.commands.middleware.CommandMiddleware._unpack_params."""

from __future__ import annotations

import pytest
from aiogram.filters import CommandObject

from raito.plugins.commands.middleware import CommandMiddleware


def _command(args: str | None) -> CommandObject:
    return CommandObject(command="cmd", args=args, prefix="/")


def test_unpack_int_params():
    mw = CommandMiddleware()
    data = mw._unpack_params(_command("2 3"), {"a": int, "b": int}, {})
    assert data == {"a": 2, "b": 3}


def test_unpack_float_and_str():
    mw = CommandMiddleware()
    data = mw._unpack_params(_command("2.5 hello"), {"x": float, "y": str}, {})
    assert data == {"x": 2.5, "y": "hello"}


def test_unpack_preserves_existing_data():
    mw = CommandMiddleware()
    data = mw._unpack_params(_command("7"), {"a": int}, {"raito": object()})
    assert data["a"] == 7
    assert "raito" in data


@pytest.mark.parametrize("token", ["true", "yes", "on", "1", "ok", "+", "TRUE", "Yes", "ON"])
def test_unpack_bool_truthy(token):
    mw = CommandMiddleware()
    data = mw._unpack_params(_command(token), {"flag": bool}, {})
    assert data["flag"] is True


@pytest.mark.parametrize("token", ["false", "no", "0", "off", "nope", "2", "-"])
def test_unpack_bool_falsy(token):
    mw = CommandMiddleware()
    data = mw._unpack_params(_command(token), {"flag": bool}, {})
    assert data["flag"] is False


def test_unpack_extra_args_ignored():
    mw = CommandMiddleware()
    data = mw._unpack_params(_command("1 2 3 4"), {"a": int}, {})
    assert data == {"a": 1}


def test_unpack_missing_arg_raises_index_error():
    mw = CommandMiddleware()
    with pytest.raises(IndexError):
        mw._unpack_params(_command("1"), {"a": int, "b": int}, {})


def test_unpack_no_args_raises_index_error():
    mw = CommandMiddleware()
    with pytest.raises(IndexError):
        mw._unpack_params(_command(None), {"a": int}, {})


def test_unpack_bad_int_raises_value_error():
    mw = CommandMiddleware()
    with pytest.raises(ValueError):
        mw._unpack_params(_command("not_a_number"), {"a": int}, {})
