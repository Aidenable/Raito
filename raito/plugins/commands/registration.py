from __future__ import annotations

from collections import defaultdict
from contextlib import suppress
from typing import TYPE_CHECKING, NamedTuple

from aiogram import Bot
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    BotCommandScopeUnion,
)
from aiogram.utils.i18n.context import gettext

from raito.plugins.roles.data import Role
from raito.utils import loggers

if TYPE_CHECKING:
    from aiogram.filters.command import Command
    from aiogram.utils.i18n.lazy_proxy import LazyProxy  # type: ignore

    from raito.plugins.roles.manager import RoleManager


__all__ = ("register_bot_commands",)


class CommandMeta(NamedTuple):
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
    role: Role | None


def extract_command_metadata(handler: HandlerObject) -> CommandMeta | None:
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
    description_str = str(description).strip()

    roles: list[Role] | None = handler.flags.get("raito__roles")
    highest_role = max(roles, key=lambda role: role.value) if roles else None

    return CommandMeta(
        command=commands[0].commands[0], description=description_str, role=highest_role
    )


def format_description(meta: CommandMeta, text: str) -> str:
    """Format description with role emoji if available.

    :param meta: CommandMeta instance
    :type meta: CommandMeta
    :param text: Description string
    :type text: str
    :return: Formatted description
    :rtype: str
    """
    if meta.role is None:
        return text
    return f"[{meta.role.emoji}] {text}"


async def _apply_bot_commands(
    bot: Bot,
    meta_entries: list[CommandMeta],
    locale: str,
    scope: BotCommandScopeUnion,
) -> None:
    """Set commands for a given scope and locale.

    :param bot: Bot instance
    :type bot: Bot
    :param meta_entries: List of command metadata
    :type meta_entries: list[CommandMeta]
    :param locale: Locale string (e.g., "en", "ru")
    :type locale: str
    :param scope: Scope for which to set commands
    :type scope: BotCommandScopeUnion
    """
    loggers.commands.debug(
        "Applying %s commands for user %s with locale %s",
        len(meta_entries),
        getattr(scope, "chat_id", None),
        locale,
    )

    bot_commands: list[BotCommand] = []
    for meta in meta_entries:
        description = meta.description
        with suppress(LookupError):
            description = gettext(description, locale=locale)

        bot_commands.append(
            BotCommand(
                command=meta.command,
                description=format_description(meta, description),
            )
        )

    await bot.set_my_commands(commands=bot_commands, scope=scope, language_code=locale)


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
    role_command_map: dict[Role | None, list[CommandMeta]] = defaultdict(list)

    for handler in handlers:
        meta = extract_command_metadata(handler)
        if meta:
            role_command_map[meta.role].append(meta)

    role_user_ids: dict[Role, list[int]] = defaultdict(list)
    for role in role_command_map:
        if role is None:
            continue

        users = await role_manager.get_users(bot.id, role)
        role_user_ids[role].extend(users)

    sorted_roles = sorted(
        (role for role in role_command_map if role is not None),
        key=lambda r: r.value,
    )
    inherited_command_map: dict[Role, list[CommandMeta]] = {}

    for i, role in enumerate(sorted_roles):
        visible_commands = []
        for lower_role in sorted_roles[: i + 1]:
            visible_commands.extend(role_command_map[lower_role])

        visible_commands.extend(role_command_map.get(None, []))
        inherited_command_map[role] = visible_commands

    for locale in locales:
        for role, user_ids in role_user_ids.items():
            commands = inherited_command_map.get(role, [])
            for user_id in user_ids:
                await _apply_bot_commands(
                    bot,
                    commands,
                    locale,
                    BotCommandScopeChat(chat_id=user_id),
                )

        await _apply_bot_commands(
            bot,
            role_command_map.get(None, []),
            locale,
            BotCommandScopeDefault(),
        )
