Stateless pagination
====================

Most pagination systems store the current page somewhere on the server. Raito's
does not — the entire state lives in the buttons. This page explains how, and
what the trade-offs are.

State lives in the callback data
--------------------------------

Every navigation button carries a ``callback_data`` that encodes the whole page
state:

.. code-block:: text

    rt_p:<mode>:<name>:<page>:<total>:<limit>

There is no server-side record of "which page is user X on". When the user taps a
button, Telegram sends that string back, and Raito reconstructs everything it
needs from it.

The round trip
--------------

#. You call :meth:`~raito.Raito.paginate` with a name, page and limit. Raito
   renders the page and draws navigation buttons whose callback data encodes the
   *target* page of each.
#. The user taps "next". Telegram delivers a callback query carrying that encoded
   state.
#. A middleware unpacks it, rebuilds the right paginator for that ``mode``, and
   injects ``paginator``, ``page``, ``limit`` and a derived
   ``offset = (page - 1) * limit`` into your handler.
#. Your handler slices *its own* data with ``offset``/``limit`` and calls
   ``paginator.answer(...)``, which edits the message and redraws navigation —
   closing the loop.

Your data is never stored by Raito; you re-slice it each time from wherever it
lives (a list, a database query, an API).

Why this is nice
----------------

- **No storage, no expiry, no cleanup.** Buttons that were sent last week still
  work; there is no session to lose.
- **Horizontally trivial.** Any process behind the bot can handle any callback,
  because the state travels with the request.
- **Simple mental model.** A page is a pure function of ``(offset, limit)`` over
  your data.

The trade-off: 64 bytes
-----------------------

Telegram limits ``callback_data`` to 64 bytes, and everything — mode, name, page,
total, limit — must fit. In practice this only bites with a long pagination
``name`` combined with large page numbers. Keep names short. Raito validates the
inputs, but the encoding is the hard ceiling, so a very long name plus big
counters can exceed the limit.

Modes
-----

The ``mode`` in the callback selects the paginator: inline (content buttons),
text, list, photo or rich. Because the mode is encoded, the middleware can
rebuild the correct paginator type on every tap without any stored context. See
the :doc:`pagination how-to <../how-to/pagination>` for the APIs.
