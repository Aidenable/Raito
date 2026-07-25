⌨️ Keyboards
============

Raito has two keyboard decorators. Both return a ready aiogram markup, so you
never manage builders or markup objects at the call site.

- :func:`@rt.keyboard.static <raito.rt.keyboard>` — declare the layout as the
  function's return value;
- :func:`@rt.keyboard.dynamic <raito.rt.keyboard>` — build it imperatively with a
  builder.

Static — layout by return value
-------------------------------

Return a list of rows. Each item is either a **button** (a ``str`` or a
``tuple``) or a **row** (a list of buttons):

.. code-block:: python

    from raito import rt


    @rt.keyboard.static(inline=False)
    def start_markup():
        return [
            "🏀 Throw a ball",           # a row with one button
            ["📄 FAQ", "🏆 Leaderboard"],  # a row with two buttons
        ]

For **inline** keyboards a button is a ``(text, value)`` tuple. ``value`` becomes
``callback_data``, unless it looks like a URL (``https://``, ``tg://``,
``t.me/...``), in which case it becomes a URL button:

.. code-block:: python

    @rt.keyboard.static(inline=True)
    def info_markup():
        return [
            ("💬 Support", "support"),                    # callback button
            [("🔒 Privacy", "privacy"), ("📄 TOS", "terms")],  # a two-button row
            ("🌐 Website", "https://example.com"),        # URL button
        ]

The decorator returns a ``ReplyKeyboardMarkup`` or ``InlineKeyboardMarkup``
depending on ``inline=``. Call the function to get the markup:

.. code-block:: python

    await message.answer("Menu:", reply_markup=start_markup())

Dynamic — build with a builder
------------------------------

When the layout depends on data, take the builder as the first argument and add
buttons yourself. Any extra parameters are yours to pass at call time:

.. code-block:: python

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from raito import rt


    @rt.keyboard.dynamic(1, 2, inline=True)
    def links_markup(builder: InlineKeyboardBuilder, privacy_url: str, tos_url: str):
        builder.button(text="💬 Support", callback_data="support")
        builder.button(text="🔒 Privacy", url=privacy_url)
        builder.button(text="📄 TOS", url=tos_url)


    await message.answer(
        "Links:",
        reply_markup=links_markup(privacy_url="...", tos_url="..."),
    )

Parameters
----------

============  =========================================================
Parameter     Meaning
============  =========================================================
``inline``    Build an inline (``True``) or reply (``False``) keyboard.
``*sizes``    Row-size pattern for ``adjust`` (e.g. ``1, 2, 1``).
``adjust``    Auto-arrange buttons with ``builder.adjust(*sizes)``.
``repeat``    Repeat the ``*sizes`` pattern to cover all buttons.
============  =========================================================

Set ``adjust=False`` to lay the keyboard out yourself — useful when the shape is
conditional:

.. code-block:: python

    @rt.keyboard.dynamic(adjust=False)
    def admin_markup(builder: InlineKeyboardBuilder, show_balance: bool = False):
        sizes = [1]
        builder.button(text="👤 Users", callback_data="users")

        if show_balance:
            builder.button(text="📤 Withdraw", callback_data="withdraw")
            builder.button(text="📥 Deposit", callback_data="deposit")
            sizes.append(2)

        builder.adjust(*sizes)
