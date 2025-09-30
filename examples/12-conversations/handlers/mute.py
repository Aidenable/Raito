from aiogram import F, Router, filters
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from raito import Raito
from raito.plugins.roles import ADMINISTRATOR, DEVELOPER, MODERATOR

router = Router(name="mute")


@router.message(filters.Command("mute"), DEVELOPER | ADMINISTRATOR | MODERATOR)
async def mute(message: Message, raito: Raito, state: FSMContext) -> None:
    await message.answer("Enter username:")
    user = await raito.wait_for(state, F.text.regexp(r"@[\w]+"))

    await message.answer("Enter duration (in minutes):")
    duration = await raito.wait_for(state, F.text.isdigit())

    while not duration.number or duration.number < 0:
        await message.answer("⚠️ Duration cannot be negative")
        duration = await duration.retry()

    await message.answer(f"✅ {user.text} will be muted for {duration.number} minutes")
