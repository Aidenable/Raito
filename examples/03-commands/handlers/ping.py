from time import perf_counter

from aiogram import Router, filters
from aiogram.types import Message

from raito import rt

router = Router(name="ping")


@router.message(filters.Command("ping"))
@rt.description("Check bot responsiveness")
@rt.hidden
async def ping(message: Message) -> None:
    started_at = perf_counter()
    msg = await message.answer("🔍 Measuring ping...")
    elapsed_ms = (perf_counter() - started_at) * 1000

    await msg.edit_text(f"🏓 Pong! <b>{elapsed_ms:.1f}ms</b>")
