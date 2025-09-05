from typing import AsyncGenerator

from aiogram import Bot, Dispatcher, Router

from raito import Raito, rt

router = Router(name="lifespan")

WEBHOOK_SECRET = "SECRET_TOKEN"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://example.com"


@rt.lifespan(router)
async def lifespan(raito: Raito, bot: Bot, dispatcher: Dispatcher) -> AsyncGenerator:
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH, secret_token=WEBHOOK_SECRET)

    bot_info = await bot.get_me()
    rt.log.info("🚀 Launching bot : [@%s] %s", bot_info.username, bot_info.full_name)

    rt.debug("Registering commands...")
    await raito.register_commands(bot)

    yield

    rt.debug("Removing webhook...")
    await bot.delete_webhook()

    rt.debug("Closing dispatcher storage...")
    await dispatcher.storage.close()

    rt.log.info("👋 Bye!")
