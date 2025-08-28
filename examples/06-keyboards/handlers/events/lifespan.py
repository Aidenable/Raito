from typing import AsyncGenerator

from aiogram import Bot, Dispatcher, Router

from raito import Raito, rt

router = Router(name="lifespan")


@rt.lifespan(router)
async def lifespan(raito: Raito, bot: Bot, dispatcher: Dispatcher) -> AsyncGenerator:
    bot_info = await bot.get_me()
    rt.log.info("🚀 Launching bot : [@%s] %s", bot_info.username, bot_info.full_name)

    rt.debug("Registering commands...")
    await raito.register_commands(bot)

    yield

    rt.debug("Removing webhook...")
    await bot.delete_webhook()

    rt.log.debug("Closing dispatcher storages...")
    await dispatcher.storage.close()
    await dispatcher.fsm.storage.close()

    rt.log.info("👋 Bye!")
