import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from raito import Raito
from raito.utils.storages.json import JSONStorage
from raito.utils.storages.sql import get_sqlite_storage

TOKEN = "TOKEN"
DEBUG = False
DEVELOPER = 1234
ROOT_DIR = Path(__file__).parent


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dispatcher = Dispatcher(storage=JSONStorage(ROOT_DIR / "fsm.json"))

SQLiteStorage = get_sqlite_storage()
sqlite_url = f"sqlite+aiosqlite:///{(ROOT_DIR / 'raito.db').as_posix()}"

raito = Raito(
    dispatcher,
    ROOT_DIR / "handlers",
    developers=[DEVELOPER],
    locales=["en"],
    production=not DEBUG,
    storage=SQLiteStorage(sqlite_url),
)
raito.init_logging()


async def main() -> None:
    await raito.setup()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
