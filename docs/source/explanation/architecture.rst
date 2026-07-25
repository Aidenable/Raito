Architecture
============

Raito is a thin layer on top of aiogram. It does not replace the dispatcher,
the FSM or the filter system — it *drives* them. Understanding that relationship
explains almost every behaviour in the library.

The ``Raito`` object
--------------------

:class:`raito.Raito` is the coordinator. When you create it you hand over the
aiogram ``Dispatcher`` and a directory of handler files:

.. code-block:: python

    raito = Raito(dispatcher, "src/handlers")

The constructor immediately does two things worth knowing about:

- it registers itself in the dispatcher's context as ``dispatcher["raito"]``, so
  every handler and filter can receive a ``raito`` argument through aiogram's
  dependency injection;
- it selects a **role provider** based on the FSM storage you passed (in-memory,
  JSON, Redis or SQL), falling back to an in-memory provider.

Nothing is loaded yet. The real work happens in :meth:`raito.Raito.setup`.

The setup sequence
------------------

``await raito.setup()`` performs, in order:

#. **Migrations** — the role provider creates its table/keys if needed.
#. **Middleware registration** — Raito attaches its middlewares to the
   dispatcher: pagination, command parsing, album grouping and conversations.
#. **Loading built-in handlers** — the ``.rt`` developer toolbox (help, router
   management, roles, stats, and the guarded eval/bash) is loaded first.
#. **Loading your routers** — the directory you passed is scanned and every
   router registered.
#. **Watchdog** — in development mode (``production=False``) a file watcher is
   started so edits reload live.

Because everything hangs off the dispatcher, Raito is transport-agnostic: it
works the same whether you poll or run behind a webhook.

How routers are discovered
--------------------------

Routers are ordinary aiogram routers that live in files. Three small classes
turn a directory into a live router tree:

``RouterParser``
    Imports a ``.py`` file as an isolated module and finds the router in it —
    either a variable named ``router`` or, failing that, the single
    ``aiogram.Router`` / ``raito.Router`` instance defined in the file.

``RouterLoader``
    Owns the lifecycle of one file: ``load`` registers the router with the
    dispatcher, ``unload`` removes it, and ``reload`` re-imports the file so new
    code takes effect. It remembers the router's position so ordering survives a
    reload.

``RouterManager``
    Scans the directory (ignoring ``_``-prefixed names), creates one loader per
    file, resolves duplicate router names, and loads everything **highest
    priority first**.

Priority and autoload
~~~~~~~~~~~~~~~~~~~~~~~

:class:`raito.Router` extends aiogram's router with two attributes:

- ``priority`` — higher loads earlier, so auth/middleware routers can register
  before the routers that depend on them;
- ``autoload`` — set to ``False`` to keep a router out of automatic loading; it
  can still be enabled at runtime with ``.rt load``.

.. code-block:: python

    from raito import Router

    router = Router(name="auth", priority=100)      # loads first
    debug = Router(name="debug", autoload=False)     # opt-in via `.rt load debug`

Hot reload
----------

In development the ``RouterManager`` runs a watcher (``watchfiles.awatch``) over
your directory. On each change it finds the loader for that file and:

- **modified** → ``reload`` (unload, re-import, load) so the new code is live;
- **added** → a loader is created for the new file and it is loaded;
- **deleted** → the router is unloaded.

The freshness of the code comes from re-importing the module on reload, not from
patching objects in place. This is why hot reload is reliable but also why
module-level side effects run again on every reload — keep import-time work in
your handler files minimal.

Features are opt-in layers
--------------------------

Everything beyond loading is added per-handler, and almost always through one of
two aiogram mechanisms:

**Flags** carry metadata on a handler. ``@rt.description``, ``@rt.hidden``,
``@rt.params`` and ``@rt.limiter`` all set flags; middlewares and the command
registrar read them later. Nothing happens at decoration time — the flag is just
data attached to the handler.

**Filters** decide whether a handler runs. The role system is the clearest
example: ``OWNER | ADMINISTRATOR`` is a filter that asks the role manager whether
the current user holds one of those roles. Used as a normal aiogram filter, it
gates the handler.

This design keeps Raito composable: you can adopt one decorator without buying
into the rest, and your handlers stay ordinary aiogram handlers.

Request-scoped by default
-------------------------

Raito leans on aiogram's per-update dependency injection. A middleware that
provides, say, a database session per update will set it up and tear it down
around each message. Raito's **scenes** are designed to preserve this: every
step of a multi-step dialog is a separate, fully-returning handler, so the
session is released between steps instead of being held while the user thinks.

**Conversations** make the opposite trade-off — ``wait_for`` suspends the
handler coroutine until the next message arrives, which is simpler but keeps that
update's dependencies alive for the duration. The
:doc:`scenes <../how-to/scenes>` and :doc:`conversations <../how-to/conversations>`
guides describe when to reach for each.
