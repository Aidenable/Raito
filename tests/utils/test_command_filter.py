import datetime as dt

import pytest
from aiogram.filters.command import CommandException, CommandObject
from aiogram.types import Chat, Message, User

from raito.utils.filters.command import PREFIX, RaitoCommand

_DATE = dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)


def _message(text):
    return Message(
        message_id=1,
        date=_DATE,
        chat=Chat(id=1, type="private"),
        from_user=User(id=1, is_bot=False, first_name="T"),
        text=text,
    )


def test_prefix_is_dot_rt():
    assert PREFIX == ".rt "
    assert RaitoCommand("test").prefix == ".rt "


def test_extract_command_splits_prefix_command_and_args():
    co = RaitoCommand.extract_command(".rt test foo bar 123")
    assert isinstance(co, CommandObject)
    assert co.prefix == ".rt "
    assert co.command == "test"
    assert co.args == "foo bar 123"


def test_extract_command_without_args():
    co = RaitoCommand.extract_command(".rt ping")
    assert co.command == "ping"
    assert co.args is None


def test_extract_command_raises_when_not_enough_parts():
    with pytest.raises(CommandException):
        RaitoCommand.extract_command(".rt")


def test_update_handler_flags_sets_raito_flag():
    flags = {}
    RaitoCommand("test").update_handler_flags(flags)
    assert flags["raito__command"] is True


async def test_filter_matches_bare_command():
    result = await RaitoCommand("test")(_message(".rt test"), bot=None)
    assert result["command"].command == "test"


async def test_filter_matches_command_with_arguments():
    result = await RaitoCommand("test")(_message(".rt test foo bar"), bot=None)
    assert result["command"].command == "test"


@pytest.mark.parametrize("text", [".rt other", "/test", ".rt testx", "test"])
async def test_filter_rejects_non_matching(text):
    result = await RaitoCommand("test")(_message(text), bot=None)
    assert result is False
