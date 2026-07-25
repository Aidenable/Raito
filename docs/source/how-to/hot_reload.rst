🔥 Hot Reload
=============

Raito automatically reloads routers on file changes in development mode.
This means you can edit handlers and see your updates **instantly — without restarting.**

How it works
------------

- Hot reload is **enabled by default** when you set `production=False`:

  .. code-block:: python

     raito = Raito(dispatcher, routers_dir="src/handlers", production=False)

- During ``raito.setup()``, Raito:
   1. Scans your ``routers_dir`` for Python files
   2. Skips files starting with ``_``
   3. Dynamically imports all routers (with ``router = Router(...)``)
   4. Starts a `watchdog <https://pypi.org/project/watchfiles/>`_ using ``watchfiles.awatch``
   5. Tracks file changes and reloads the corresponding routers

- No need to manually call ``include_router()`` or manage imports

----------

Example
~~~~~~~~~~

.. code-block:: python

   from aiogram import Router
   from aiogram.types import Message
   from aiogram.filters import Command

   router = Router(name="debug")

   @router.message(Command("debug"))
   async def debug_handler(message: Message):
       await message.answer("Hello, this is a live-reloading handler!")

Edit the message and hit save — it will reload automatically.

----------

What happens on file change?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- If a ``.py`` file is **modified or created**:
   - The corresponding router is **unloaded and loaded**
- If a ``.py`` file is **deleted**:
   - The router is **unregistered**

Each router is uniquely tracked by ``Router.name``.

--------

Telegram Raito Commands
~~~~~~~~~~~~~~~~~~~~~~~
You can also manage routers **manually via Telegram chat**:

- ``.rt routers`` — List all registered routers
- ``.rt unload <router_name>`` — Unload a router by name
- ``.rt load <router_name>`` — Load a router by name
- ``.rt reload <router_name>`` — Reload an existing router

--------

Limitations
~~~~~~~~~~~
- Changes to **shared modules** (e.g. ``utils/``, ``models/``) do not trigger reloads
- Reloads affect only files in ``routers_dir``
- If a router has side-effects at the top level (e.g., DB queries) — they may run twice
