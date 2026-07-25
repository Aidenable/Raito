🔦 Raito
========

*REPL, hot-reload, keyboards, pagination, and internal dev tools — all in one.*

**Raito** is a batteries-included companion for `aiogram <https://aiogram.dev>`_.
It removes the boilerplate from bot development: routers load themselves, change
live while the bot runs, and ship with roles, pagination, multi-step scenes,
keyboards, throttling and a set of in-chat developer tools.

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


Where to start
--------------

The documentation is organised in four parts, each answering a different need.

:doc:`🐣 Tutorial <tutorial/index>`
    Learning-oriented. Build your first Raito bot from an empty folder and grow
    it step by step. **Start here if you are new.**

:doc:`🛠️ How-to guides <how-to/index>`
    Task-oriented recipes. "How do I add roles / paginate a list / build a
    keyboard?" Short, focused answers for things you already understand.

:doc:`📖 Reference <reference/index>`
    Information-oriented. The generated API, configuration options and the
    in-chat ``.rt`` commands. Look things up here.

:doc:`💡 Explanation <explanation/index>`
    Understanding-oriented. How hot-reload, request-scoped scenes and the role
    system actually work under the hood.


.. note::

    New to the four-part split? It follows the `Diátaxis <https://diataxis.fr>`_
    framework: tutorials teach, how-to guides solve a task, reference describes
    the machinery, and explanation gives you the mental model.


.. toctree::
    :hidden:
    :caption: Tutorial

    tutorial/installation
    tutorial/your-first-bot
    tutorial/commands
    tutorial/access-control
    tutorial/going-further

.. toctree::
    :hidden:
    :caption: How-to guides

    how-to/routers
    how-to/hot_reload
    how-to/commands
    how-to/roles
    how-to/keyboards
    how-to/pagination
    how-to/scenes
    how-to/conversations
    how-to/album
    how-to/throttling
    how-to/lifespan
    how-to/logging
    how-to/retry
    how-to/truncate
    how-to/suppress_not_modified

.. toctree::
    :hidden:
    :caption: Reference

    reference/api
    reference/configuration
    reference/commands

.. toctree::
    :hidden:
    :caption: Explanation

    explanation/architecture
    explanation/hot-reload
    explanation/scenes-vs-conversations
    explanation/role-model
    explanation/stateless-pagination
