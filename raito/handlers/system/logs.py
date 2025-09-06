from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

from aiogram import Router, html

from raito.plugins.commands import description, hidden, params
from raito.plugins.roles.roles import DEVELOPER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.types import Message

    from raito.core.raito import Raito

router = Router(name="raito.system.logs")


@router.message(RaitoCommand("logs"), DEVELOPER)
@description("Show system logs")
@params(lines=int)
@hidden
async def logs(message: Message, lines: int, raito: Raito) -> None:
    if getattr(raito, "_tf_handler", None) is None:
        await message.answer(text="Logs retention is disabled")
        return

    lines = 0 if lines < 1 else lines
    logs = raito._tf_handler.get_logs(lines)
    logs_text = ""
    for line in logs:
        logs_text += f"{line}\n"
        if len(logs_text) > 4096:
            break
    await message.answer(text=html.pre(escape(logs_text)), parse_mode="HTML")
