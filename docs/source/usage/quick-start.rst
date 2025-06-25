🚀 Quick Start
==========

Minimal setup to get your bot running with **Raito**:

.. code-block:: python

    import asyncio

    from aiogram import Bot, Dispatcher
    from raito import Raito

    async def main() -> None:
        bot = Bot(token="TOKEN")
        dispatcher = Dispatcher()
        raito = Raito(dispatcher, "src/handlers")

        await raito.setup()
        await dispatcher.start_polling(bot)

    if __name__ == "__main__":
        asyncio.run(main())

What's happening here?
-----------------------

- ``Raito(...)`` sets up watchdog, middlewares, managers, etc.
- It auto-loads routers from the `"src/handlers"` folder.
- You don't need to register routers manually.

-----------------------

.. tip::
    Try adding a file like `src/handlers/ping.py`

.. code-block:: python

   from aiogram import Router
   from aiogram.types import Message
   from aiogram.filters import Command

   router = Router(name="ping")

   @router.message(Command("ping"))
   async def ping(message: Message):
       await message.answer("Pong! 🏓")

📦 Not installed yet? See :doc:`installation`
