from aiogram.types import Message

from raito import Router

# Loads before all other routers due to high priority.
# Useful for middleware, filters, or shared state that others depend on.
router = Router(name="auth", priority=100)


@router.message()
async def catch_all(message: Message) -> None:
    await message.answer("Access denied.")
