from dataclasses import dataclass
from random import randint, sample

from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from raito import rt

router = Router(name="leaderboard")


@dataclass
class Player:
    number: int
    score: int


@rt.keyboard.dynamic(adjust=False)
def leaderboard_markup(builder: InlineKeyboardBuilder, players: list[Player]) -> None:
    adjust = []

    for i, player in enumerate(players, start=1):
        match i:
            case 1:
                medal = "🥇 "
            case 2:
                medal = "🥈 "
            case 3:
                medal = "🥉 "
            case _:
                medal = ""

        text = f"{medal}#{player.number} — {player.score}"
        builder.button(text=text, callback_data=f"player:{player.number}")

        if i <= 3:
            adjust.append(1)
        elif i % 2 == 0:
            adjust.append(2)

    builder.button(text="◀️", callback_data="left")
    builder.button(text="↩️ Back", callback_data="back")
    builder.button(text="▶️", callback_data="right")
    adjust.append(3)

    builder.adjust(*adjust)


def _get_players(total: int) -> list[Player]:
    numbers = sample(range(10, 1000), total)
    scores = sorted((randint(50, 300) * i for i in range(1, total + 1)), reverse=True)
    return [Player(number=num, score=score) for num, score in zip(numbers, scores)]


@router.message(F.text == "🏆 Leaderboard")
async def leaderboard(message: Message) -> None:
    players = _get_players(21)
    await message.answer("<b>🏆 Leaderboard</b>", reply_markup=leaderboard_markup(players))
