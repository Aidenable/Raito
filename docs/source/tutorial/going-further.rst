Going further
=============

You can now build described, typed, role-gated commands that hot-reload as you
edit. Here is the rest of Raito, and where to read about it.

Interactive features
--------------------

- **Keyboards** — build inline and reply keyboards declaratively or with a
  builder. See the :doc:`keyboards guide <../how-to/keyboards>`.
- **Pagination** — page through text and media with inline buttons, with **no
  server-side state**. See the :doc:`pagination guide <../how-to/pagination>`.
- **Scenes** — multi-step dialogs where every step is an ordinary handler, so
  request-scoped dependencies (like a database session) are released between
  messages. See the :doc:`scenes guide <../how-to/scenes>`.
- **Conversations** — pause a handler and wait for the user's next message. See
  the :doc:`conversations guide <../how-to/conversations>`.

Operational features
--------------------

- **Throttling** — rate-limit globally or per-command.
- **Albums** — receive grouped media as a single list.
- **Lifespan** — startup/shutdown logic in one async generator.
- **Storages** — optional JSON and SQL persistence.

Understand the internals
------------------------

If you prefer to know *why* things work the way they do, the
:doc:`../explanation/index` section covers the architecture, the hot-reload
mechanism, request-scoped scenes, stateless pagination and the role model.

Look things up
--------------

The :doc:`../reference/index` has the generated API, every configuration option
and the full list of in-chat ``.rt`` commands.
