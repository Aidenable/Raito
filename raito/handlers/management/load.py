from asyncio import sleep
from typing import TYPE_CHECKING

from aiogram import Router, html
from aiogram.types import Message

from raito.plugins.roles import Role, roles
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from raito.core.raito import Raito

router = Router(name="raito.management.load")


@router.message(RaitoCommand("load"))
@roles(Role.DEVELOPER)
async def load_router(message: Message, raito: "Raito") -> None:
    args = message.text
    name_position = 3

    if args is None or len(args.split()) != name_position:
        await message.answer("⚠️ Please provide a valid router name")
        return

    router_name = args.split()[name_position - 1]
    router_loader = raito.router_manager.loaders.get(router_name)
    if not router_loader:
        await message.answer(f"🔎 Router {html.bold(router_name)} not found", parse_mode="HTML")
        return

    msg = await message.answer(f"📦 Loading router {html.bold(router_name)}...", parse_mode="HTML")
    router_loader.load()
    await sleep(0.5)
    await msg.edit_text(f"✅ Router {html.bold(router_name)} loaded", parse_mode="HTML")
