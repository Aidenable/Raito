📖 Pagination
=============================

Need to paginate a long list of items?

Raito provides a built-in system for inline, text, photo, list, and rich-message pagination — simple and fully customized.

--------

Features
--------

- Predefined paginator types (inline, text, photo, list, rich)
- Auto-generated navigation
- Loop navigation (wrap around first/last)
- Declarative handler with ``@rt.on_pagination(...)``
- Flexible API and pluggable paginator types

---------

Quick Start
-----------

1. Invoking Pagination
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    @router.message(filters.CommandStart())
    async def start(message: Message, raito: Raito, bot: Bot) -> None:
        if not message.from_user:
            return

        await raito.paginate(
            "my_pagination_name",
            chat_id=message.chat.id,
            bot=bot,
            from_user=message.from_user,
            total_pages=10,
            limit=5,
        )

2. Handling Pagination Events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To respond to page changes, use the ``@rt.on_pagination(...)`` decorator:

.. code-block:: python

   @rt.on_pagination(router, "my_pagination_name")
   async def on_pagination(
       query: CallbackQuery,
       paginator: InlinePaginator,
       offset: int,
       limit: int,
   ):
       buttons = [InlineKeyboardButton(text=str(i), callback_data=f"button_{i}") for i in range(offset, offset + limit)]
       await paginator.answer("Button list:", buttons=buttons)

---------

Paginator Types
----------------

Pick the paginator with ``mode=`` (defaults to ``PaginationMode.INLINE``):

- ``PaginationMode.INLINE`` — :class:`InlinePaginator`, text plus a row of content buttons above the navigation.
- ``PaginationMode.TEXT`` — :class:`TextPaginator`, plain text.
- ``PaginationMode.PHOTO`` — :class:`PhotoPaginator`, a photo with a caption.
- ``PaginationMode.LIST`` — :class:`ListPaginator`, a list of strings joined by a separator.
- ``PaginationMode.RICH`` — :class:`RichPaginator`, structured `Rich Messages <https://core.telegram.org/bots/api#richmessage>`_ — headings, lists, tables, code blocks, and more. Requires ``aiogram>=3.30.0``.

.. code-block:: python

    await raito.paginate(
        "rich_docs",
        chat_id=message.chat.id,
        bot=bot,
        from_user=message.from_user,
        mode=PaginationMode.RICH,
        total_pages=3,
    )


    @rt.on_pagination(router, "rich_docs")
    async def on_rich_pagination(query: CallbackQuery, paginator: RichPaginator, page: int) -> None:
        await paginator.answer(rich_message=InputRichMessage(blocks=PAGES[page]))

---------

Navigation
----------

Each paginator generates a default navigation row.

Raito merges this with your custom buttons automatically:

- If ``buttons`` only — adds default navigation
- If ``buttons`` + ``reply_markup`` — combines both
- If ``reply_markup`` only — uses it directly

To manually attach navigation:

.. code-block:: python

   builder = InlineKeyboardBuilder()
   navigation = paginator.build_navigation()

   builder.attach(builder.from_markup(navigation))
   builder.button(text="Back", callback_data="menu")

---------

Under the Hood
--------------

- All callbacks use this format: ``rt_p:mode:name:page:total:limit``
- `PaginatorMiddleware` parses data and injects:
   - ``paginator``, ``offset``, ``limit``, ``page``
- Everything is type-safe and based on ``IPaginator`` protocol
- You can build custom paginators and plug them in
