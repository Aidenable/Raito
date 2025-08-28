⌨️ Keyboard Factory
===================

Raito comes with two decorators for building keyboards declaratively:

- ``@keyboard.static`` — for simple static layouts
- ``@keyboard.dynamic`` — for flexible builder-style keyboards

No need to manually manage builders or markup objects — just write declarative logic.

----------

``@keyboard.static``
~~~~~~~~~~~~~~~~~

Use this when you want to **declare layout via return value**.

.. code-block:: python

   from raito import rt

   @rt.keyboard.static(inline=False)
   def start_markup():
       return [
           ["🏀 Throw a ball"],
           [["📄 FAQ"], ["🏆 Leaderboard"]],
       ]

Each item is either:

- A ``str`` or ``tuple`` — becomes a single button
- A list of such items — becomes a row

.. tip::
    Returns a ``ReplyKeyboardMarkup`` or ``InlineKeyboardMarkup`` depending on ``inline=`` param.

----------

``@keyboard.dynamic``
~~~~~~~~~~~~~~~~~~

Use this when you need to **build keyboards programmatically**.

.. code-block:: python

   from aiogram.utils.keyboard import InlineKeyboardBuilder
   from raito import rt

   @rt.keyboard.dynamic(inline=True)
   def faq_markup(builder: InlineKeyboardBuilder, tos_url: str, privacy_url: str):
       builder.button(text="Terms of Service", url=tos_url)
       builder.button(text="Privacy", url=privacy_url)

.. tip::
   You get the builder as the **first argument**. Everything else is up to you.

------

Parameters
~~~~~~~~~~

Both decorators accept optional arguments:

- ``inline=True`` — whether to build inline or reply keyboard
- ``adjust=True`` — whether to auto-adjust layout using ``builder.adjust()``
- ``repeat=True`` — if True, ``adjust(*sizes)`` will repeat the pattern
- ``*sizes`` — pattern for button row sizes (e.g., ``2, 2, 1``)

.. code-block:: python

   @rt.keyboard.dynamic(2, 2, 1, inline=False, repeat=False)
   def markup(builder: ReplyKeyboardBuilder):
       ...

-------

Examples
~~~~~~~~~~~~

Static layout:
^^^^^^^^^^^^^^^^

.. code-block:: python

   from raito import rt

   @rt.keyboard.static(inline=True)
   def faq_buttons():
       return [
           ("Terms of Service", "tos"),
           ("Privacy", "privacy"),
       ]

Dynamic layout:
^^^^^^^^^^^^^^^^

.. code-block:: python

   from aiogram.utils.keyboard import InlineKeyboardBuilder
   from raito import rt

   from ... import Player

   @rt.keyboard.dynamic()
   def leaderboard(builder: InlineKeyboardBuilder, players: list[Player]):
       for player in players:
           builder.button(text=f"{player.name}", callback_data=f"player:{player.id}")

       builder.adjust(1, 2, 2)

Dynamic pagination-like example:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from aiogram.utils.keyboard import InlineKeyboardBuilder
   from raito import rt

   from ... import Player

   @rt.keyboard.dynamic(adjust=False)
   def leaderboard(builder: InlineKeyboardBuilder, players: list[Player]):
       for i, player in enumerate(players, start=1):
           builder.button(text=f"#{i} {player.name}", callback_data=f"player:{player.id}")

       builder.button(text="◀️", callback_data="prev")
       builder.button(text="▶️", callback_data="next")

       builder.adjust(3)
