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

router = Router(name="raito.management.unload")


@router.message(RaitoCommand("unload"), DEVELOPER)
@description("Unloads a router by name")
@params(name=str)
@hidden
async def unload_router(message: Message, raito: Raito, name: str) -> None:
    router_loader = raito.router_manager.loaders.get(name)
    if not router_loader:
        await message.answer(f"🔎 Router {html.bold(name)} not found", parse_mode="HTML")
        return

    msg = await message.answer(
        f"📦 Unloading router {html.bold(name)}...",
        parse_mode="HTML",
    )
    router_loader.unload()
    await sleep(0.5)
    await msg.edit_text(f"✅ Router {html.bold(name)} unloaded", parse_mode="HTML")
