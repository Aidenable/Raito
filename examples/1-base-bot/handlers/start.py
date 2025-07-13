from aiogram import Router, filters
from aiogram.types import Message

router = Router(name="start")


@router.message(filters.CommandStart())
async def start(message: Message) -> None:
    await message.answer("Hello!")
