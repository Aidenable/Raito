🖼️ Album
=============================

Handling Telegram media groups (albums) is tricky — Aiogram calls your handler for **each photo/video separately**.
This leads to duplicated logic and messy grouping.

Raito provides a drop-in middleware to handle albums cleanly.

--------

What it does
------------

- Groups incoming messages by ``media_group_id``
- Delays processing until **all media parts** are received
- Injects a full album as ``data["album"]`` into your handler

--------

Example
-------

.. code-block:: python

   from aiogram import F
   from aiogram.types import Message

   @router.message(F.photo)
   async def handle_album(message: Message, album: list[Message] | None = None):
       if album is None:
           await message.answer("You sent a single photo!")
           return

       await message.answer(f"You sent {len(album)} photos!")

--------

Tips
~~~~

- Works with photos, videos, documents — anything with `media_group_id`
- `album` is `None` for single media
- Use it with any filters and flags
