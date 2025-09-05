from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from raito import Raito

TOKEN = "TOKEN"
HANDLERS_DIR = Path(__file__).parent / "handlers"
DEBUG = False

WEBHOOK_SECRET = "SECRET_TOKEN"
WEBHOOK_PATH = "/webhook"
WEB_SERVER_HOST = "localhost"
WEB_SERVER_PORT = 8080

bot = Bot(token=TOKEN)
dispatcher = Dispatcher()
raito = Raito(dispatcher, HANDLERS_DIR, developers=[], locales=["en"], production=not DEBUG)
raito.init_logging()


async def _on_startup(_: web.Application):
    await raito.setup()


def main() -> None:
    app = web.Application()
    app.on_startup.append(_on_startup)

    handler = SimpleRequestHandler(dispatcher=dispatcher, bot=bot, secret_token=WEBHOOK_SECRET)
    handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dispatcher, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, print=None)


if __name__ == "__main__":
    main()
