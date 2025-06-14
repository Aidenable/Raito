from typing import TYPE_CHECKING

from aiogram import Router, html
from aiogram.types import Message

from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from raito.core.raito import Raito

router = Router(name="raito.management.load")


@router.message(RaitoCommand("load"))
async def load_router(message: Message, raito: "Raito") -> None:
    args = message.text
    if args is None or len(args.split()) != 3:
        await message.answer("Please provide a valid router name")
        return

    router_name = args.split()[2]
    router_loader = raito.manager.loaders.get(router_name)
    if not router_loader:
        await message.answer(f"Router <b>{html.bold(router_name)}</b> not found", parse_mode="HTML")
        return

    router_loader.load()
    await message.answer(f"Loading router <b>{html.bold(router_name)}</b>...", parse_mode="HTML")
