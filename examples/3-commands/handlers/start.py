from aiogram import Router, filters
from aiogram.types import Message

from raito import rt

router = Router(name="start")


@router.message(filters.CommandStart())
@rt.description("Start command")
async def start(message: Message) -> None:
    await message.answer("Hello!")
