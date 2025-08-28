from aiogram import Router, filters
from aiogram.types import Message
from roles.filters import DUROV

from raito import rt
from raito.plugins.roles import ADMINISTRATOR, DEVELOPER, OWNER

router = Router(name="admin")


@router.message(filters.Command("admin"), DEVELOPER | OWNER | ADMINISTRATOR | DUROV)
@rt.description("Admin menu")
async def admin(message: Message) -> None:
    await message.answer("⚙️ Admin-Menu")
