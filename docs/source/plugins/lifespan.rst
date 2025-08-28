🍃 Lifespan
===========

Raito lets you define async startup/shutdown logic using a ``@rt.lifespan(router)`` decorator — just like in FastAPI.

---------

Example
~~~~~~~

.. code-block:: python

   from typing import AsyncGenerator

   from aiogram import Bot, Router,
   from raito import rt, Raito

   router = Router(name="lifespan")

   @rt.lifespan(router)
   async def lifespan_fn(raito: Raito, bot: Bot):
       bot_info = await bot.get_me()
       rt.log.info("🚀 Launching bot : [@%s] %s", bot_info.username, bot_info.full_name)

       rt.debug("Registering commands...")
       await raito.register_commands(bot)

       yield

       rt.log.info("👋 Bye!")


---------

How it works
~~~~~~~~~~~~~

- Code before ``yield`` runs on **startup**
- Code after ``yield`` runs on **shutdown**
- Lifespans are tracked per ``bot.id`` and executed in reverse order on exit
