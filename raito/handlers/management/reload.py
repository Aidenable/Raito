from __future__ import annotations

from asyncio import sleep
from typing import TYPE_CHECKING

from aiogram import Router, html

from raito.plugins.commands import description, hidden, params
from raito.plugins.roles.roles import DEVELOPER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.types import Message

    from raito.core.raito import Raito

router = Router(name="raito.management.reload")


@router.message(RaitoCommand("reload"), DEVELOPER)
@description("Reloads a router by name")
@params(name=str)
@hidden
async def reload_router(message: Message, raito: Raito, name: str) -> None:
    router_loader = raito.router_manager.loaders.get(name)
    if not router_loader:
        await message.answer(
            f"🔎 Router <b>{html.bold(name)}</b> not found",
            parse_mode="HTML",
        )
        return

    msg = await message.answer(
        f"📦 Reloading router <b>{html.bold(name)}</b>...",
        parse_mode="HTML",
    )
    await router_loader.reload()
    await sleep(0.5)
    await msg.edit_text(f"✅ Router {html.bold(name)} reloaded", parse_mode="HTML")
