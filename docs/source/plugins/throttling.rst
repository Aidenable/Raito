🐢 Throttling
=============================

Sometimes users spam buttons or commands.

Raito includes built-in throttling to prevent flooding.

You can:

- Set a **global** delay for all handlers
- Set **per-handler** rate limits with ``@rt.limiter(...)``
- Choose how throttling is scoped: by user, chat, or bot

---------

Usage
------

To apply throttling globally:

.. code-block:: python

   from raito import Raito

   raito = rt.Raito(...)
   raito.add_throttling(1.2, mode="user")

This will prevent the same user from triggering *any handler* more than once every 1.2 seconds.

---------

Per-Handler Limits
~~~~~~~~~~~~~~~~~~~~

For fine-grained control, use ``@rt.limiter``:

.. code-block:: python

   from raito import rt

   @router.message(Command("status"))
   @rt.limiter(rate_limit=3.0, mode="chat")
   async def status(message: Message): ...

---------

Modes
------

Available throttling modes:

- ``"user"`` — limits per user
- ``"chat"`` — limits per chat
- ``"bot"`` — one cooldown shared across all users

---------

Behavior
---------

- **Global throttling** is applied first
- If a handler has ``@rt.limiter(...)``, that **overrides** the global rule
- Events are ignored (not rejected or delayed) if throttled
