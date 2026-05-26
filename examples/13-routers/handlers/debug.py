from aiogram import filters
from aiogram.types import Message

from raito import Router

# Not loaded on startup. Enable via: .rt load debug
router = Router(name="debug", autoload=False)


@router.message(filters.Command("debug"))
async def debug(message: Message) -> None:
    await message.answer("Debug router is active.")
