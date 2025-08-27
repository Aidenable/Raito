from __future__ import annotations

from collections import defaultdict
from contextlib import suppress
from typing import TYPE_CHECKING, NamedTuple

from aiogram import Bot
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    BotCommandScopeUnion,
)
from aiogram.utils.i18n.context import gettext

from raito.plugins.roles.data import RoleData
from raito.utils import loggers

if TYPE_CHECKING:
    from aiogram.filters.command import Command
    from aiogram.utils.i18n.lazy_proxy import LazyProxy  # type: ignore

    from raito.plugins.roles.manager import RoleManager


__all__ = ("register_bot_commands",)


class _CommandMeta(NamedTuple):
    """Command metadata.

    :param command: Command name (without prefix)
    :type command: str
    :param description: Localized or plain description
    :type description: str
    :param role: Minimum required role (if any)
    :type role: Role | None
    """

    command: str
    description: str
    roles: list[RoleData]


def _extract_command_metadata(handler: HandlerObject) -> _CommandMeta | None:
    """Extract command metadata from a handler's flags.

    :param handler: Message handler object
    :type handler: HandlerObject
    :return: CommandMeta instance or None
    :rtype: CommandMeta | None
    """
    commands: list[Command] | None = handler.flags.get("commands")
    if not commands or not commands[0].commands:
        return None

    if handler.flags.get("raito__hidden"):
        return None

    description: LazyProxy | str | None = handler.flags.get("raito__description", "—")
    roles: list[RoleData] | None = handler.flags.get("raito__roles")

    return _CommandMeta(
        command=commands[0].commands[0],
        description=str(description).strip(),
        roles=roles or [],
    )


def _format_description(meta: _CommandMeta, text: str) -> str:
    """Format description with role emoji if available.

    :param meta: CommandMeta instance
    :type meta: CommandMeta
    :param text: Description string
    :type text: str
    :return: Formatted description
    :rtype: str
    """
    if not meta.roles:
        return text

    emojis = "".join([r.emoji for r in meta.roles])
    return f"[{emojis}] {text}"


async def _apply_bot_commands(
    bot: Bot,
    meta_entries: list[_CommandMeta],
    scope: BotCommandScopeUnion,
    locale: str | None = None,
) -> None:
    """Set commands for a given scope and locale.

    :param bot: Bot instance
    :type bot: Bot
    :param meta_entries: List of command metadata
    :type meta_entries: list[_CommandMeta]
    :param locale: Locale string (e.g., "en", "ru")
    :type locale: str
    :param scope: Scope for which to set commands
    :type scope: BotCommandScopeUnion
    """
    loggers.commands.debug(
        "Setting %d command(s) for scope=%s, locale='%s'",
        len(meta_entries),
        getattr(scope, "chat_id", "default"),
        locale or "default",
    )

    bot_commands: list[BotCommand] = []
    for meta in meta_entries:
        description = meta.description
        with suppress(LookupError):
            description = gettext(description, locale=locale)

        bot_commands.append(
            BotCommand(
                command=meta.command,
                description=_format_description(meta, description),
            )
        )

    try:
        await bot.set_my_commands(commands=bot_commands, scope=scope, language_code=locale)
    except TelegramBadRequest as exc:
        loggers.commands.warning(
            "Failed to set commands for scope=%s, locale='%s': %s",
            getattr(scope, "chat_id", "default"),
            locale or "default",
            exc,
        )


async def register_bot_commands(
    role_manager: RoleManager,
    bot: Bot,
    handlers: list[HandlerObject],
    locales: list[str],
) -> None:
    """Register localized bot commands across roles and user scopes.

    :param role_manager: RoleManager instance
    :type role_manager: RoleManager
    :param bot: Aiogram Bot instance
    :type bot: Bot
    :param handlers: List of message handler objects
    :type handlers: list[HandlerObject]
    :param locales: List of supported locales (e.g., "en", "ru")
    :type locales: list[str]
    """
    role_commands: dict[str | None, list[_CommandMeta]] = defaultdict(list)

    for handler in handlers:
        meta = _extract_command_metadata(handler)
        if not meta:
            continue

        if not meta.roles:
            role_commands[None].append(meta)

        for role in meta.roles:
            role_commands[role.slug].append(meta)

    role_users: dict[str, set[int]] = defaultdict(set)
    for role_slug in role_commands:  # type: ignore
        if role_slug is None:
            continue

        users = await role_manager.get_users(bot.id, role_slug)
        role_users[role_slug].update(users)

    for locale in locales:
        for role_slug, users in role_users.items():
            commands = role_commands.get(role_slug, [])
            for user_id in users:
                await _apply_bot_commands(
                    bot=bot,
                    meta_entries=commands,
                    scope=BotCommandScopeChat(chat_id=user_id),
                    locale=locale,
                )

        await _apply_bot_commands(
            bot=bot,
            meta_entries=role_commands.get(None, []),
            scope=BotCommandScopeDefault(),
            locale=locale,
        )

    await _apply_bot_commands(
        bot=bot,
        meta_entries=role_commands.get(None, []),
        scope=BotCommandScopeDefault(),
        locale=None,
    )
