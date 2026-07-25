Access control with roles
=========================

Raito ships a role system so you can gate commands behind access levels without
writing your own checks.

Built-in roles
--------------

Nine roles come predefined. Import them from ``rt`` and use them as aiogram
filters:

.. code-block:: python

    from aiogram import Router, filters, types
    from raito import rt
    from raito.rt import OWNER, ADMINISTRATOR, MODERATOR

    router = Router(name="moderation")


    @router.message(filters.Command("ban"), OWNER | ADMINISTRATOR | MODERATOR)
    @rt.description("Ban a user")
    @rt.params(user_id=int)
    async def ban(message: types.Message, user_id: int, bot: Bot) -> None:
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
        await message.answer("✅ User banned")

A role used as a filter passes only if the user currently holds that role.
Combine roles with ``|`` to mean "any of these".

The full list — ``OWNER``, ``DEVELOPER``, ``ADMINISTRATOR``, ``MODERATOR``,
``MANAGER``, ``SPONSOR``, ``GUEST``, ``SUPPORT``, ``TESTER`` — and how to define
your own is in the :doc:`roles guide <../how-to/roles>`.

Developers
----------

Pass trusted user IDs as ``developers`` when constructing Raito. They implicitly
hold the ``developer`` role — handy for yourself during development:

.. code-block:: python

    raito = Raito(dispatcher, "my_bot/handlers", developers=[123456789])

Assigning roles at runtime
--------------------------

Roles are stored by a provider chosen from your FSM storage (in-memory by
default; SQLite/PostgreSQL/Redis/JSON when configured). A user with a managing
role can grant roles to others straight from the chat:

.. code-block:: text

    .rt roles      → opens a role picker, then asks for a user ID
    .rt revoke     → removes a user's role
    .rt staff      → lists everyone and their roles

These ``.rt`` commands are part of Raito's built-in developer toolbox — see the
:doc:`commands reference <../reference/commands>`.

.. warning::

    A user with ``developer`` role can run ``.rt eval`` and ``.rt bash``
    (arbitrary code / shell) — but only if the bot was started with
    ``Raito(..., enable_dangerous_commands=True)``. Keep that flag off unless you
    understand the risk.

That's the core loop: files become routers, decorators add behaviour, roles gate
access. :doc:`going-further` points you at the bigger features.
