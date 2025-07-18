import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from roles.manager import CustomRoleManager

from raito.core.raito import Raito
from raito.plugins.roles.providers.json import JSONRoleProvider
from raito.utils.configuration import RaitoConfiguration
from raito.utils.storages.json import JSONStorage

TOKEN = "TOKEN"
HANDLERS_DIR = Path(__file__).parent / "handlers"
DEBUG = False
DEVELOPERS = [1234]
ROOT_DIR = Path(__file__).parent

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dispatcher = Dispatcher()

json_storage = JSONStorage(ROOT_DIR / "raito.json")
raito = Raito(
    dispatcher,
    HANDLERS_DIR,
    developers=DEVELOPERS,
    production=not DEBUG,
    configuration=RaitoConfiguration(
        role_manager=CustomRoleManager(
            provider=JSONRoleProvider(json_storage),
            developers=DEVELOPERS,
        ),
    ),
)
raito.init_logging()


async def main() -> None:
    await raito.setup()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
