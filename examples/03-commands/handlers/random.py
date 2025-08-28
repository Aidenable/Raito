from random import randint

from aiogram import Router, filters
from aiogram.types import Message

from raito import rt

router = Router(name="random")


@router.message(filters.Command("random"))
@rt.description("Generate a number between two given values")
@rt.params(num1=int, num2=int)
async def random(message: Message, num1: int, num2: int) -> None:
    low, high = sorted((num1, num2))
    result = randint(low, high)

    await message.answer(f"🎲 <b>{result}</b>")
