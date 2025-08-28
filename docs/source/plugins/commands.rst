⚙️ Commands
========================

Raito adds power features to command handlers via flags, middleware, and auto-registration.

- ``@rt.description(...)`` — adds descriptions for Telegram slash-command list
- ``@rt.hidden`` — hides handlers from the command list
- ``@rt.params(...)`` — extracts and validates command parameters
- Automatic middleware for parameter parsing
- Auto-registration via ``raito.register_commands(...)``

-----

Descriptions
~~~~~~~~~~~~

Use ``@rt.description()`` to attach a localized (or plain) description to a command.

.. code-block:: python

   from aiogram import Router
   from aiogram.types import Message
   from aiogram.filters import Command
   from raito import rt

   router = Router(name="ban")

   @router.message(Command("ban"))
   @rt.description("Ban a user by ID")
   async def ban(message: Message):
       ...

This will be used during command registration.

-----

Hidden commands
~~~~~~~~~~~~~~~

Use ``@rt.hidden`` to exclude a handler from the command list.

.. code-block:: python

   @router.message(Command("debug"))
   @rt.hidden
   async def debug(message: Message):
       ...

-----

Parameter Parsing
~~~~~~~~~~~~~~~~~

Use ``@rt.params(...)`` to automatically parse parameters from ``/command arg1 arg2``.

.. code-block:: python

   @router.message(Command("ban"))
   @rt.params(user_id=int)
   async def ban(message: Message, user_id: int):
       await message.answer(f"🔨 User {user_id} banned.")

Supported types: ``str``, ``int``, ``bool``, ``float``

If a param is missing or invalid, Raito will:
- Show an auto-generated help message (with ``description``)
- Or trigger a custom error event via ``raito.command_parameters_error``

-----

Auto-Registration
~~~~~~~~~~~~~~~~~

Once you use the flags, just call:

.. code-block:: python

   await raito.register_commands(bot)

It will:

- Collect all handlers
- Use their flags (description, roles, hidden, etc.)
- Register scoped commands for different roles and locales

Raito will also:
- Group commands by role
- Assign different command lists to different users
- Add role emojis to descriptions (e.g., ``[👑] Ban a user``)

-----

Localization
~~~~~~~~~~~~

Descriptions support ``LazyProxy`` from ``aiogram.utils.i18n``. If you use i18n context:

.. code-block:: python

   @rt.description(__("Ban a user"))
   def ...

Raito will localize this during command registration for each locale.
