🗂 Routers
=========

Raito uses an extended ``Router`` class on top of aiogram's built-in router.
It adds **priority-based loading**, **autoload control**, and seamless integration with the hot reload system.

---------

Basic usage
~~~~~~~~~~~

.. code-block:: python

   from raito import Router

   router = Router(name="my_router")

   @router.message()
   async def handler(message):
       await message.answer("Hello!")

Raito will automatically discover and register this router if the file is inside ``routers_dir``.

---------

Parameters
~~~~~~~~~~

.. code-block:: python

   router = Router(
       name="my_router",
       priority=10,
       autoload=True,
   )

- ``name`` — unique router name; if omitted, Raito derives it from the filename
- ``priority`` — load order: **higher values load first** (default: ``0``)
- ``autoload`` — if ``False``, the router is discovered but not loaded on startup (default: ``True``)

---------

Priority
~~~~~~~~

When multiple routers are present, they load in descending priority order.
Routers with the same priority load in alphabetical file order.

.. code-block:: python

   # loaded first
   router = Router(name="auth", priority=100)

.. code-block:: python

   # loaded after auth
   router = Router(name="general", priority=0)

This matters when one router has filters or middleware that others depend on.

---------

Autoload
~~~~~~~~

Set ``autoload=False`` to register a router without activating it at startup.
You can then load it manually via Telegram commands or ``RouterLoader``.

.. code-block:: python

   router = Router(name="debug", autoload=False)

.. code-block:: text

   .rt load debug

---------

Naming & conflicts
~~~~~~~~~~~~~~~~~~

Each router must have a unique name across ``routers_dir``.
If two files expose a router with the same name, Raito renames the second one automatically:

.. code-block:: text

   WARNING: Duplicate router name: handler. Will rename to handler_0x7f3a1b2c...

To avoid this, always set an explicit ``name``:

.. code-block:: python

   router = Router(name="shop_catalog")

---------

Additional methods
~~~~~~~~~~~~~~~~~~

``Router`` inherits everything from aiogram's ``Router`` and adds:

- ``router.on_pagination(name, *filters)`` — register a pagination callback handler
- ``router.on_command_signature_error()`` — handle incorrect command usage
- ``router.lifespan()`` — define startup/shutdown logic (see :doc:`lifespan`)
