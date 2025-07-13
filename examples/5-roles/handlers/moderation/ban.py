from aiogram import Bot, Router, filters
from aiogram.types import Message

from raito import rt
from raito.plugins.roles.roles import ADMINISTRATOR, DEVELOPER, MODERATOR, OWNER

router = Router(name="ban")


@router.message(filters.Command("ban"), DEVELOPER | OWNER | ADMINISTRATOR | MODERATOR)
@rt.description("Ban a chat member by ID")
@rt.params(user_id=int)
async def ban(message: Message, user_id: int, bot: Bot) -> None:
    await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
    await message.answer("🛑 User has been <b>banned</b> successfully.")
