"""Tests for :class:`InlinePaginator.answer`."""

from __future__ import annotations

from aiogram.methods import SendMessage
from aiogram.types import InlineKeyboardMarkup, Message

from raito.plugins.pagination.enums import PaginationMode


def test_inline_mode(make_paginator):
    paginator = make_paginator()
    assert paginator.mode is PaginationMode.INLINE


async def test_answer_sends_message_when_no_existing(make_paginator, bot, make_message):
    paginator = make_paginator(current_page=1, total_pages=3)
    bot.add_result_for(SendMessage, ok=True, result=make_message("sent"))

    returned = await paginator.answer("Hello page")

    assert isinstance(returned, Message)

    request = bot.get_request()
    assert isinstance(request, SendMessage)
    assert request.text == "Hello page"
    assert request.chat_id == paginator.chat_id
    # Navigation keyboard is attached automatically.
    assert isinstance(request.reply_markup, InlineKeyboardMarkup)


async def test_answer_stores_existing_message(make_paginator, bot, make_message):
    paginator = make_paginator()
    assert paginator.existing_message is None

    result_message = make_message("sent")
    bot.add_result_for(SendMessage, ok=True, result=result_message)

    await paginator.answer("First render")

    # The freshly sent message is cached for subsequent edits.
    assert paginator.existing_message is result_message
