🐢 Throttling
=============

Rate-limit handlers so users can't flood the bot. Raito offers a global limit,
per-handler limits, and three scoping modes.

Global throttling
-----------------

:meth:`~raito.Raito.add_throttling` installs one limit across every message and
callback query:

.. code-block:: python

    raito = Raito(dispatcher, "handlers")
    raito.add_throttling(1.2, mode="user")

Now the same user can trigger *any* handler at most once every 1.2 seconds. The
default mode is ``"chat"``.

Per-handler limits
------------------

For a specific handler, apply :func:`@rt.limiter <raito.rt.limiter>`:

.. code-block:: python

    from aiogram import filters, types
    from raito import rt


    @router.message(filters.Command("export"))
    @rt.limiter(rate_limit=5.0, mode="user")
    async def export(message: types.Message) -> None:
        ...

Its default mode is ``"user"``. A handler carrying ``@rt.limiter`` uses **only**
its own limit — it bypasses the global one, so you can make one expensive command
stricter (or looser) than the rest without touching the global rule.

Modes
-----

============  =========================================================
Mode          Cooldown is shared by…
============  =========================================================
``"user"``    the same user (across chats).
``"chat"``    the same chat (all members share one cooldown).
``"bot"``     everyone — a single global cooldown for the whole bot.
============  =========================================================

Behaviour and limits
--------------------

- A throttled update is **silently dropped** — the handler is not called and the
  user gets no error. Keep limits short enough not to feel broken.
- Limits are enforced with a ``cachetools.TTLCache``; ``add_throttling`` accepts
  ``max_size`` (default ``10_000``) to cap how many keys are tracked.
- The per-handler limit is remembered by the handler's identity, so its rate is
  fixed at first use — changing ``rate_limit`` for the same handler at runtime
  won't take effect until restart.
