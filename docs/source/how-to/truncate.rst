✂️ truncate
=============

Shorten a string to a maximum length, appending an ellipsis when it is cut.

.. code-block:: python

    from raito.utils.helpers.truncate import truncate

    truncate("Hello, world!", 8)            # "Hello..."
    truncate("short", 8)                     # "short"        (unchanged)
    truncate("Hello, world!", 8, ellipsis="…")  # "Hello, …"

Signature: ``truncate(text, max_length, ellipsis="...")``. When ``text`` is
longer than ``max_length``, the result is cut so that ``text`` plus ``ellipsis``
fits within the limit.

Raito uses it internally to keep command descriptions and help output within
Telegram's length limits — reach for it whenever you echo user- or
config-provided text into a fixed-width UI.

.. note::

    Give ``max_length`` room for the ellipsis. With a limit smaller than the
    ellipsis itself the result can exceed ``max_length`` — size the limit for the
    UI you're targeting.
