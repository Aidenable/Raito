from asyncio import sleep
from typing import TYPE_CHECKING

from aiogram import Router, html
from aiogram.types import Message

from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from raito.core.raito import Raito

router = Router(name="raito.management.reload")


@router.message(RaitoCommand("reload"))  # type: ignore[misc]
async def reload_router(message: Message, raito: "Raito") -> None:
    args = message.text
    if args is None or len(args.split()) != 3:
        await message.answer("⚠️ Please provide a valid router name")
        return

    router_name = args.split()[2]
    router_loader = raito.manager.loaders.get(router_name)
    if not router_loader:
        await message.answer(
            f"🔎 Router <b>{html.bold(router_name)}</b> not found", parse_mode="HTML"
        )
        return

    msg = await message.answer(
        f"📦 Reloading router <b>{html.bold(router_name)}</b>...", parse_mode="HTML"
    )
    await router_loader.reload()
    await sleep(0.5)
    await msg.edit_text(f"✅ Router {html.bold(router_name)} reloaded", parse_mode="HTML")
