from asyncio import sleep

from aiogram import Router, filters
from aiogram.types import Message

from raito import rt

router = Router(name="start")


@router.message(filters.Command("export"))
@rt.description("Export something")
@rt.limiter(5, mode="user")
async def export(message: Message):
    msg = await message.answer("📦 Exporting your data, please wait...")
    await sleep(5)
    await msg.edit_text("<b>❇️ Done!</b> https://example.com/data.csv")
