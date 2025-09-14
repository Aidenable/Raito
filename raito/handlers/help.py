from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

from aiogram import Dispatcher, Router, html
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, LinkPreviewOptions

from raito import Raito, rt
from raito.plugins.commands import description, hidden
from raito.plugins.pagination.enums import PaginationMode
from raito.plugins.pagination.paginators.list import ListPaginator
from raito.plugins.roles import DEVELOPER
from raito.utils.filters import RaitoCommand
from raito.utils.helpers.truncate import truncate

if TYPE_CHECKING:
    from aiogram.types import Message

router = Router(name="raito.help")


def _iter_raito_commands(
    dispatcher: Dispatcher,
) -> Generator[tuple[list[Command], HandlerObject], None, None]:
    for router in dispatcher.chain_tail:
        for handler in router.message.handlers:
            commands: list[Command] | None = handler.flags.get("commands")
            if handler.flags.get("raito__command") and commands:
                yield commands, handler


def _format_handler(command: Command, handler: HandlerObject) -> str:
    params: dict[str, type] = handler.flags.get("raito__params", {})
    params_str = " ".join(f"[{name}]" for name in params)

    signature = f"{command.prefix}{command.commands[0]} {params_str}"
    description: str = truncate(handler.flags.get("raito__description", ""), max_length=96)

    return html.code(signature) + "\n" + html.blockquote(html.italic(description))


def _get_formatted_commands(dispatcher: Dispatcher) -> list[str]:
    return [
        _format_handler(commands[0], handler)
        for commands, handler in _iter_raito_commands(dispatcher)
        if len(commands) > 0
    ]


@router.message(RaitoCommand("help"), DEVELOPER)
@description("Lists Raito commands")
@hidden
async def help_handler(message: Message, raito: Raito, command: CommandObject) -> None:
    if not message.bot or not message.from_user:
        return

    if command.args:
        for commands, handler in _iter_raito_commands(raito.dispatcher):
            if len(commands) <= 0:
                continue

            main_command = commands[0]
            if command.args in main_command.commands:
                await message.answer(_format_handler(main_command, handler), parse_mode="HTML")
                return

        await message.answer("⚠️ Command not found")
        return

    limit = 5
    raito_commands = _get_formatted_commands(raito.dispatcher)

    await raito.paginate(
        name="raito__commands",
        chat_id=message.chat.id,
        bot=message.bot,
        from_user=message.from_user,
        mode=PaginationMode.LIST,
        limit=limit,
        total_pages=ListPaginator.calc_total_pages(len(raito_commands), limit),
    )


@rt.on_pagination(router, "raito__commands", DEVELOPER)
async def on_pagination(
    _: CallbackQuery,
    raito: Raito,
    paginator: ListPaginator,
    offset: int,
    limit: int,
) -> None:
    commands = _get_formatted_commands(raito.dispatcher)
    footer = html.italic(html.link("Powered by Raito", "https://github.com/Aidenable/Raito"))

    await paginator.answer(
        items=[*commands[offset : offset + limit], footer],
        separator="\n\n",
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
