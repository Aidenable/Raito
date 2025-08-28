✏️ SuppressNotModifiedError
=============================

Editing messages with the same content raises ``TelegramBadRequest``.

Use this context manager to silently suppress ``"message is not modified"`` errors:

.. code-block:: python

   from raito.utils.errors import SuppressNotModifiedError

   with SuppressNotModifiedError():
       await message.edit_text("same text")
