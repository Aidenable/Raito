import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from raito import Raito

TOKEN = "TOKEN"
HANDLERS_DIR = Path(__file__).parent / "handlers"
DEBUG = False
DEVELOPER = 1234

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dispatcher = Dispatcher()
raito = Raito(
    dispatcher, HANDLERS_DIR, developers=[DEVELOPER], locales=["en"], production=not DEBUG
)
raito.init_logging("aiogram.dispatcher", "watchfiles.main")


async def main() -> None:
    await raito.setup()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
