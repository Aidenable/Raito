💬 Conversations
================

Building multi-step dialogs in Telegram bots is often clunky.

Raito provides a lightweight way to wait for the **next user message** in a clean, linear style.

.. warning::

   Conversations DO NOT work with ``Dispatcher.events_isolation``,
   since ``SimpleEventIsolation`` operates with a ``asyncio.Lock`` on active handlers,
   and ``wait_for`` will never receive an update.


--------

Example
-------

.. code-block:: python

    from aiogram import F, Router, filters
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

    from raito import Raito

    router = Router(name="mute")


    @router.message(filters.Command("mute"))
    async def mute(message: Message, raito: Raito, state: FSMContext) -> None:
        await message.answer("Enter username:")
        user = await raito.wait_for(state, F.text.regexp(r"@[\w]+"))

        await message.answer("Enter duration (in minutes):")
        duration = await raito.wait_for(state, F.text.isdigit())

        while not duration.number or duration.number < 0:
            await message.answer("⚠️ Duration cannot be negative")
            duration = await duration.retry()

        await message.answer(f"✅ {user.text} will be muted for {duration.number} minutes")

--------

How it works
------------

- Each ``wait_for`` call registers a pending conversation in Raito’s internal registry
- A conversation entry stores:

  - A ``Future`` (to resume your handler later)
  - The filters to check incoming messages
- When a message arrives:

  - Raito checks for an active conversation bound to that ``FSMContext.key``
  - If filters match, the future is completed and returned to your handler
