from asyncio import sleep

from aiogram import Bot, Router, filters
from aiogram.types import Message

from raito import Raito, rt

router = Router(name="start")


@router.message(filters.CommandStart())
@rt.description("Start command")
async def start(message: Message, raito: Raito, bot: Bot) -> None:
    if not message.from_user:
        return

    is_durov = await raito.role_manager.has_role(bot.id, message.from_user.id, "durov")
    if is_durov:
        msg = await message.answer(
            "Need a smart bot framework that doesn’t crash when your code does?\n"
            "Try <i>Raito</i> — now with <b>99.9%</b> uptime (the other 0.1% is your fault)\n"
            "\n"
            "<i>Sponsored by Raito®</i> #advertisement"
        )
        await sleep(10)
        await msg.delete()

    await message.answer("Hello!")
