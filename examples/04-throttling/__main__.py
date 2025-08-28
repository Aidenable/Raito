import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from raito import Raito

TOKEN = "TOKEN"
HANDLERS_DIR = Path(__file__).parent / "handlers"
DEBUG = False

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dispatcher = Dispatcher()
raito = Raito(dispatcher, HANDLERS_DIR, developers=[], locales=["en"], production=not DEBUG)
raito.init_logging()
raito.add_throttling(0.5, mode="chat")


async def main() -> None:
    await raito.setup()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
