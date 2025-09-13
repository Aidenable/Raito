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

Static inline keyboard:
^^^^^^^^^^^^^^^^

.. code-block:: python

   from raito import rt

   @rt.keyboard.static()
   def info_markup():
       return [
           [("💬 Support", "support")],
           [("🔒 Privacy", "privacy"), ("📄 TOS", "terms_of_use")]
       ]

    @router.message(...)
    async def handler(message: Message):
        await message.answer("Buttons:", reply_markup=info_markup())

Static reply keyboard:
^^^^^^^^^^^^^^^^

.. code-block:: python

    from raito import rt

    @rt.keyboard.static(inline=False)
    def info_markup():
        return [
            ["💬 Support"],
            [["🔒 Privacy"], ["📄 TOS"]]
        ]

    @router.message(...)
    async def handler(message: Message):
        await message.answer("Buttons:", reply_markup=info_markup())

Dynamic inline keyboard:
^^^^^^^^^^^^^^^^

.. code-block:: python

   from aiogram.utils.keyboard import InlineKeyboardBuilder
   from raito import rt

   @rt.keyboard.dynamic(1, 2)
   def info_markup(builder: InlineKeyboardBuilder, privacy_url: str, tos_url: str):
       builder.button(text="💬 Support", callback_data="support")
       builder.button(text="🔒 Privacy", url=privacy_url)
       builder.button(text="📄 TOS", url=tos_url)

    @router.message(...)
    async def handler(message: Message):
        await message.answer("Buttons:", reply_markup=info_markup(
            privacy_url="https://example.com/privacy",
            tos_url="https://example.com/tos",
        ))

Dynamic reply keyboard:
^^^^^^^^^^^^^^^^

.. code-block:: python

    from aiogram.utils.keyboard import ReplyKeyboardBuilder
    from raito import rt

    @rt.keyboard.dynamic(1, 2, inline=False)
    def info_markup(builder: ReplyKeyboardBuilder):
        builder.button(text="💬 Support")
        builder.button(text="🔒 Privacy")
        builder.button(text="📄 TOS")

    @router.message(...)
    async def handler(message: Message):
        await message.answer("Buttons:", reply_markup=info_markup())

Custom adjust:
^^^^^^^^^^^^^^^^

.. code-block:: python

   from aiogram.utils.keyboard import InlineKeyboardBuilder
   from raito import rt

   @rt.keyboard.dynamic(adjust=False)
   def admin_markup(builder: InlineKeyboardBuilder, show_balance_management: bool = False):
       adjust = []

       builder.button(text="👤 Users", callback_data="users")
       adjust.append(1)

       if show_balance_management:
           builder.button(text="📤 Withdraw", callback_data="withdraw")
           builder.button(text="📥 Deposit", callback_data="deposit")
           adjust.append(2)

       builder.adjust(*adjust)

    @router.message(...)
    async def handler(message: Message):
        await message.answer("Buttons:", reply_markup=admin_markup(True))
