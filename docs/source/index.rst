🔦 That's Raito!
=============

*REPL, hot-reload, keyboards, pagination, and internal dev tools — all in one.*

Features
~~~~~~~~

- :doc:`Hot Reload <plugins/hot_reload>` — automatic router loading and file watching for instant development cycles
- :doc:`Role System <plugins/roles>` — pre-configured roles (owner, support, tester, etc) and selector UI
- :doc:`Pagination <plugins/pagination>` — easy pagination over text and media using inline buttons
- **FSM Toolkit** — interactive confirmations, questionnaires, and mockable message flow
- **CLI Generator** — ``$ raito init`` creates a ready-to-use bot template in seconds
- :doc:`Keyboard Factory <plugins/keyboards>` — static and dynamic generation
- :doc:`Command Registration <plugins/commands>` — automatic setup of bot commands with descriptions for each
- :doc:`Album Support <plugins/album>` — groups media albums and passes them to handlers
- :doc:`Rate Limiting <plugins/throttling>` — apply global or per-command throttling via decorators or middleware
- **Database Storages** — optional JSON & SQL support
- **REPL** — execute async Python in context (``_msg``, ``_user``, ``_raito``)
- :doc:`Params Parser <plugins/commands>` — extracts and validates command arguments
- :doc:`Logging Formatter <utils/logging>` — beautiful, readable logs out of the box
- **Metrics** — inspect memory usage, uptime, and caching stats


-------------------


🚀 Quick Start
~~~~~~~~~~~

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

Contents
--------
.. toctree::
    :maxdepth: 1

    installation
    quick_start
    plugins/index
    utils/index
