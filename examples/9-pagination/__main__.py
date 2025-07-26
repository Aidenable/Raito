import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from raito.core.raito import Raito
from raito.utils.configuration import (
    PaginationControls,
    PaginationStyle,
    PaginationTextFormat,
    RaitoConfiguration,
)

TOKEN = "TOKEN"
HANDLERS_DIR = Path(__file__).parent / "handlers"
DEBUG = False

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dispatcher = Dispatcher()
raito = Raito(
    dispatcher,
    HANDLERS_DIR,
    developers=[],
    locales=["en"],
    production=not DEBUG,
    configuration=RaitoConfiguration(
        pagination_style=PaginationStyle(
            controls=PaginationControls(previous="<", next=">"),
            text_format=PaginationTextFormat(counter_template="Page {current} of {total}"),
        )
    ),
)
raito.init_logging()


async def main() -> None:
    await raito.setup()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
