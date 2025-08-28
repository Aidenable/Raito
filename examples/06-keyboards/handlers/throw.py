from aiogram import F, Router
from aiogram.types import Message

router = Router(name="throw")


@router.message(F.text == "🏀 Throw a ball")
async def throw(message: Message) -> None:
    await message.answer_dice(emoji="🏀")
