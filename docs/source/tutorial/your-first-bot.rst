Your first bot
==============

Let's build a minimal bot and understand what Raito does for you.

Project layout
--------------

Create a folder for your handlers next to your entry point:

.. code-block:: text

    my_bot/
    ├── __main__.py
    └── handlers/
        └── start.py

The entry point
---------------

``__main__.py`` wires aiogram together and hands the ``handlers`` directory to
Raito:

.. code-block:: python

    import asyncio

    from aiogram import Bot, Dispatcher
    from raito import Raito


    async def main() -> None:
        bot = Bot(token="YOUR_TOKEN")
        dispatcher = Dispatcher()

        raito = Raito(dispatcher, "my_bot/handlers", production=False)

        raito.init_logging()
        await raito.setup()
        await dispatcher.start_polling(bot)


    if __name__ == "__main__":
        asyncio.run(main())

Two calls do the work:

- :meth:`raito.Raito.setup` scans ``my_bot/handlers`` and registers every router
  it finds — you never call ``dispatcher.include_router`` yourself.
- ``production=False`` turns on the **watchdog**: edit a handler file and Raito
  reloads it without restarting the bot.

:meth:`raito.Raito.init_logging` is optional — it installs a colored,
readable log formatter.

A handler
---------

Each file in ``handlers/`` exposes a ``router`` object. Raito also accepts a
router under any variable name, or the single router defined in the file — but
``router`` is the convention.

.. code-block:: python

    # my_bot/handlers/start.py
    from aiogram import Router, filters, types

    router = Router(name="start")


    @router.message(filters.CommandStart())
    async def start(message: types.Message) -> None:
        await message.answer("Hello from Raito! 👋")

Run it:

.. code-block:: bash

    python -m my_bot

Send ``/start`` to your bot and you'll get a reply. Now edit the text in
``start.py`` and save — the change is live on the next message, no restart.

.. tip::

    Files and folders whose names start with ``_`` are ignored by the loader, so
    ``handlers/_utils.py`` won't be treated as a router.

What just happened
------------------

* Raito walked ``handlers/`` recursively, imported each module and picked up its
  router.
* It registered them with the dispatcher in a deterministic order.
* In development mode it started watching the folder for changes.

Curious how the reload works? See
:doc:`../explanation/architecture`. Ready to add real commands? Continue to
:doc:`commands`.
