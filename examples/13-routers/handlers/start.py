from aiogram import filters
from aiogram.types import Message

from raito import Router, rt

router = Router(name="start")


@router.message(filters.CommandStart())
@rt.description("Start the bot")
async def start(message: Message) -> None:
    await message.answer("Hello! This example shows router priorities and autoload control.")
