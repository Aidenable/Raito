🖼️ Albums
===========

Telegram delivers a media group (an album) as **one update per item**, so a
naive handler runs once per photo. Raito's album middleware collects the parts
and hands your handler the whole group at once.

It is installed automatically by :meth:`~raito.Raito.setup` — there is nothing to
wire up.

Receiving an album
------------------

Declare an ``album`` parameter. When a message is part of a media group, Raito
injects the full list; for a single item it is not injected, so your default
applies:

.. code-block:: python

    from aiogram import F, types

    router = Router(name="media")


    @router.message(F.photo)
    async def on_photo(message: types.Message, album: list[types.Message] | None = None):
        if album is None:
            await message.answer("You sent a single photo.")
            return

        await message.answer(f"You sent an album of {len(album)} items.")

The album is delivered to the handler that matches the **first** message of the
group, and the list preserves arrival order. Works for any grouped media —
photos, videos, documents.

How the grouping works
----------------------

The first message of a group opens a short collection window (``delay``, ~0.6 s
by default). Every other update with the same ``media_group_id`` that arrives
during the window is added to the list and suppressed; when the window closes the
first message's handler runs with the complete ``album``. See
:doc:`../explanation/architecture` for the middleware model.

.. tip::

    Because the group is assembled by a timer, a very large album or slow network
    can occasionally split it. Treat ``album`` as "the items we had a moment to
    collect", and don't assume a fixed count.
