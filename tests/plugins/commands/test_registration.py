"""Tests for raito.plugins.commands.registration.register_bot_commands."""

from __future__ import annotations

import types

import pytest
from aiogram.methods import SetMyCommands
from aiogram.types import BotCommandScopeChat, BotCommandScopeDefault

from raito.plugins.commands.registration import register_bot_commands
from raito.plugins.roles.data import RoleData

ADMIN = RoleData(slug="admin", name="Admin", description="Admins", emoji="X")


def _handler(command, *, description=None, roles=None, hidden=False):
    """Build a HandlerObject-like stub carrying the relevant flags."""
    flags = {"commands": [types.SimpleNamespace(commands=[command])]}
    if description is not None:
        flags["raito__description"] = description
    if roles is not None:
        flags["raito__roles"] = roles
    if hidden:
        flags["raito__hidden"] = True
    return types.SimpleNamespace(flags=flags)


class StubRoleManager:
    """Minimal role manager exposing the awaited ``get_users`` API."""

    def __init__(self, mapping):
        self._mapping = mapping

    async def get_users(self, bot_id, slug):
        return set(self._mapping.get(slug, set()))


def _queue_responses(bot, count=50):
    for _ in range(count):
        bot.add_result_for(SetMyCommands, ok=True, result=True)


def _requests(bot):
    return list(bot.session.requests)


def _commands_for_default(requests):
    names = set()
    for req in requests:
        if isinstance(req.scope, BotCommandScopeDefault):
            names.update(c.command for c in req.commands)
    return names


def _commands_for_chat(requests, chat_id):
    names = set()
    for req in requests:
        if isinstance(req.scope, BotCommandScopeChat) and req.scope.chat_id == chat_id:
            names.update(c.command for c in req.commands)
    return names


async def test_public_commands_go_to_default_scope(bot):
    _queue_responses(bot)
    handlers = [_handler("ping", description="Ping")]

    await register_bot_commands(StubRoleManager({}), bot, handlers, locales=[])

    requests = _requests(bot)
    assert any(isinstance(r.scope, BotCommandScopeDefault) for r in requests)
    assert _commands_for_default(requests) == {"ping"}


async def test_hidden_commands_are_never_registered(bot):
    _queue_responses(bot)
    handlers = [
        _handler("ping", description="Ping"),
        _handler("secret", description="Secret", hidden=True),
    ]

    await register_bot_commands(StubRoleManager({"admin": {111}}), bot, handlers, locales=[])

    all_names = {c.command for r in _requests(bot) for c in r.commands}
    assert "secret" not in all_names
    assert "ping" in all_names


async def test_role_user_gets_public_and_role_commands(bot):
    _queue_responses(bot)
    handlers = [
        _handler("ping", description="Ping"),
        _handler("ban", description="Ban", roles=[ADMIN]),
    ]

    await register_bot_commands(StubRoleManager({"admin": {111}}), bot, handlers, locales=[])

    requests = _requests(bot)

    # The role user's chat scope has BOTH public and role commands.
    assert _commands_for_chat(requests, 111) == {"ping", "ban"}

    # The default (public) scope only has the public command.
    assert _commands_for_default(requests) == {"ping"}
    assert "ban" not in _commands_for_default(requests)


async def test_role_description_gets_emoji_prefix(bot):
    _queue_responses(bot)
    handlers = [_handler("ban", description="Ban", roles=[ADMIN])]

    await register_bot_commands(StubRoleManager({"admin": {111}}), bot, handlers, locales=[])

    ban_descriptions = [
        c.description for r in _requests(bot) for c in r.commands if c.command == "ban"
    ]
    assert ban_descriptions
    assert all(d.startswith("[X]") for d in ban_descriptions)


async def test_users_without_roles_get_no_chat_scope(bot):
    _queue_responses(bot)
    handlers = [_handler("ping", description="Ping")]

    # No role has any users assigned.
    await register_bot_commands(StubRoleManager({}), bot, handlers, locales=[])

    requests = _requests(bot)
    assert not any(isinstance(r.scope, BotCommandScopeChat) for r in requests)


async def test_locales_produce_language_specific_requests(bot):
    _queue_responses(bot)
    handlers = [
        _handler("ping", description="Ping"),
        _handler("ban", description="Ban", roles=[ADMIN]),
    ]

    await register_bot_commands(
        StubRoleManager({"admin": {111}}), bot, handlers, locales=["en", "ru"]
    )

    requests = _requests(bot)
    languages = {r.language_code for r in requests}
    assert "en" in languages
    assert "ru" in languages
    # Role user still sees both commands in each localized chat scope.
    assert _commands_for_chat(requests, 111) == {"ping", "ban"}


async def test_default_scope_only_when_no_commands(bot):
    _queue_responses(bot)

    # Handler with an empty command list is skipped entirely.
    empty = types.SimpleNamespace(flags={"commands": [types.SimpleNamespace(commands=[])]})

    await register_bot_commands(StubRoleManager({}), bot, [empty], locales=[])

    all_names = {c.command for r in _requests(bot) for c in r.commands}
    assert all_names == set()


@pytest.mark.parametrize("locales", [[], ["en"]])
async def test_queue_is_sufficient(bot, locales):
    _queue_responses(bot)
    handlers = [_handler("ping", description="Ping")]

    # Should not raise IndexError from an exhausted response queue.
    await register_bot_commands(StubRoleManager({}), bot, handlers, locales=locales)
