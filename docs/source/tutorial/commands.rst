Commands with descriptions and arguments
=========================================

A bot is mostly commands. Raito adds three small decorators from the ``rt``
namespace that make commands self-describing and type-safe.

Descriptions
------------

:func:`rt.description <raito.rt.description>` attaches a human description to a
command. Raito collects these and registers them with Telegram, so they show up
in the client's slash menu automatically.

.. code-block:: python

    from aiogram import Router, filters, types
    from raito import rt

    router = Router(name="ping")


    @router.message(filters.Command("ping"))
    @rt.description("Check that the bot is alive")
    async def ping(message: types.Message) -> None:
        await message.answer("pong 🏓")

To publish the menu, call :meth:`raito.Raito.register_commands` once at startup
(usually from a :doc:`lifespan <../how-to/lifespan>` handler):

.. code-block:: python

    await raito.register_commands(bot)

Hiding a command
----------------

Some commands are internal. Decorate them with
:func:`rt.hidden <raito.rt.hidden>` (note: no parentheses) and they are
registered as handlers but kept out of the
`slash command menu <https://core.telegram.org/bots/features#commands>`_:

.. code-block:: python

    @router.message(filters.Command("debug"))
    @rt.hidden
    async def debug(message: types.Message) -> None:
        ...

Typed arguments
---------------

For a command like ``/add 2 3``, :func:`rt.params <raito.rt.params>` extracts
positional arguments, converts them to the declared types and injects them into
your handler by name:

.. code-block:: python

    @router.message(filters.Command("add"))
    @rt.description("Add two numbers")
    @rt.params(a=int, b=int)
    async def add(message: types.Message, a: int, b: int) -> None:
        await message.answer(f"{a} + {b} = {a + b}")

Supported types are ``int``, ``float``, ``str`` and ``bool`` (``bool`` accepts
``true/yes/on/1/ok/+``). If an argument is missing or fails to convert, Raito
replies with an auto-generated usage message instead of calling your handler —
so ``/add two 3`` shows help, not a traceback.

.. tip::

    Arguments are **positional** and split on whitespace, in declaration order.
    ``@rt.params(name=str)`` with ``/hello John Doe`` gives ``name="John"``, so
    use a single trailing argument for multi-word input, or parse
    ``message.text`` yourself.

.. important::

    Positional command arguments fit developer and testing tools, not
    user-facing flows. ``/add 2 3`` is fine for you; asking ordinary users to
    pass arguments in the right order is not friendly. To collect input from
    real users, ask one thing at a time with a
    :doc:`scene <../how-to/scenes>` (backed by FSM) or a
    :doc:`conversation <../how-to/conversations>` (``wait_for``).

You now have described, typed commands. Next, restrict who can call them in
:doc:`access-control`.
