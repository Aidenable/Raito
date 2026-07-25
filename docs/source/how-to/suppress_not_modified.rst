✏️ SuppressNotModifiedError
=============================

Editing a message to content it already has makes Telegram raise
``TelegramBadRequest: message is not modified``. That is usually harmless — you
re-rendered a screen that happened not to change — but it crashes the handler.

Wrap the edit in the context manager to swallow exactly that error:

.. code-block:: python

    from raito.utils.errors import SuppressNotModifiedError

    with SuppressNotModifiedError():
        await message.edit_text("same text")

Only the "message is not modified" ``TelegramBadRequest`` is suppressed; every
other error — including other ``TelegramBadRequest`` variants — propagates
normally.

When to use it
--------------

Any place that re-renders on every interaction and might redraw an identical
screen: refreshing an inline menu, a live-updating status message, or paginating
back to the current page. Raito's own paginators use it internally, so you rarely
need it there — reach for it in your own edit-in-place UIs.

.. tip::

    It is also exposed on ``rt``, so ``from raito import rt`` then
    ``with rt.SuppressNotModifiedError(): ...`` works without a deeper import.
