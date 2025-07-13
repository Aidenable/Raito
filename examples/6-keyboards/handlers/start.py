from aiogram import Router, filters
from aiogram.types import Message

from raito import rt

router = Router(name="start")


@rt.keyboard.static(inline=False)
def start_markup() -> list:
    return [
        ["🏀 Throw a ball"],
        [["📄 FAQ"], ["🏆 Leaderboard"]],
    ]


@router.message(filters.CommandStart())
@rt.description("Show the main menu")
async def start(message: Message) -> None:
    await message.answer(
        "Welcome to the <b>🏀 Basketball Championship</b>!",
        reply_markup=start_markup(),
    )
