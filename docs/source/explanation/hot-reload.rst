How hot reload works
====================

In development Raito reloads a handler file the moment you save it, without
restarting the bot. This page explains the machinery so you know what it can and
can't do.

The three actors
----------------

``RouterParser``
    Imports one file as an **isolated module**. It builds a spec from the file
    path, gives the module a unique synthetic name, registers it in
    ``sys.modules`` *before* executing it (so dataclasses and relative machinery
    resolve), runs the module, and returns the router it finds.

``RouterLoader``
    Owns a single file's lifecycle:

    - ``load`` includes the router in the dispatcher;
    - ``unload`` removes it and drops the parsed router;
    - ``reload`` runs ``unload`` then ``load``.

    Crucially, ``unload`` records the router's **index** among the dispatcher's
    sub-routers, and ``load`` restores it — so a reload keeps the router in the
    same position, preserving handler resolution order.

``RouterManager``
    Scans the directory, creates one loader per file, and runs the watcher.

The reload cycle
----------------

When a file changes, the manager finds its loader and calls ``reload``:

#. ``unload`` — the router is removed from the dispatcher and its parsed object
   is dropped (set to ``None``).
#. ``load`` — accessing the loader's router **re-imports the file**, so the new
   code is parsed fresh, then the router is re-registered at its saved index.

Freshness comes from *re-importing the module*, not from patching objects in
place. That is what makes reload reliable: you always get exactly the code on
disk.

What reloads cleanly — and what doesn't
----------------------------------------

- **Handler bodies** reload transparently. Editing what a handler does is safe
  even for a user mid-:doc:`scene <../how-to/scenes>`, because aiogram identifies
  an FSM step by its string name, not by the Python object.
- **New files** are picked up: an ``added`` event creates a loader and loads the
  router.
- **Deleted files** unload their router.
- **Module-level side effects run again** on every reload, because the module is
  re-executed. Keep import-time work in handler files minimal — build expensive
  state in a :doc:`lifespan <../how-to/lifespan>`, not at module top level.
- **Shared modules** (a helper imported by several routers) don't themselves
  trigger a reload of the routers that import them; only the changed router file
  reloads.

Why development only
--------------------

The watcher (``watchfiles.awatch``) runs only when ``production=False``. In
production you want a fixed, audited set of routers and none of the file-watching
overhead, so ``setup`` simply loads once and never starts the watcher.

Priority and ordering
---------------------

At startup routers load **highest priority first**, which fixes their order in
the dispatcher. A reload restores a router to its previous index, so ordering is
stable across edits. A brand-new file added at runtime is appended rather than
priority-inserted — restart to re-establish strict priority order if it matters.
