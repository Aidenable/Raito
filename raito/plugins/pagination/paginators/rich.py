from __future__ import annotations

from typing import TYPE_CHECKING

from raito.plugins.pagination.enums import PaginationMode
from raito.utils.errors import SuppressNotModifiedError

from .base import BasePaginator

if TYPE_CHECKING:
    from aiogram.types import (
        InlineKeyboardMarkup,
        InputRichMessage,
        Message,
        ReplyParameters,
    )

__all__ = ("RichPaginator",)


class RichPaginator(BasePaginator):
    """Rich message paginator."""

    @property
    def mode(self) -> PaginationMode:
        """Get rich pagination mode.

        :return: pagination mode
        :rtype: PaginationMode
        """
        return PaginationMode.RICH

    async def answer(
        self,
        rich_message: InputRichMessage,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        allow_paid_broadcast: bool | None = None,
        message_effect_id: str | None = None,
        reply_parameters: ReplyParameters | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> Message:
        """Send or edit paginated rich message.

        :param rich_message: rich message content
        :type rich_message: InputRichMessage
        :param disable_notification: disable notification
        :type disable_notification: bool | None
        :param protect_content: protect content
        :type protect_content: bool | None
        :param allow_paid_broadcast: allow paid broadcast
        :type allow_paid_broadcast: bool | None
        :param message_effect_id: message effect id
        :type message_effect_id: str | None
        :param reply_parameters: reply parameters
        :type reply_parameters: ReplyParameters | None
        :param reply_markup: custom reply markup
        :type reply_markup: InlineKeyboardMarkup | None
        :return: paginated message
        :rtype: Message
        :raises RuntimeError: if bot instance not set
        """
        if not self.bot:
            raise RuntimeError("Bot not set via PaginatorMiddleware")

        reply_markup = reply_markup or self.build_navigation()

        if self.existing_message is None:
            self.existing_message = await self.bot.send_rich_message(
                chat_id=self.chat_id,
                rich_message=rich_message,
                disable_notification=disable_notification,
                protect_content=protect_content,
                allow_paid_broadcast=allow_paid_broadcast,
                message_effect_id=message_effect_id,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
            )
        else:
            with SuppressNotModifiedError():
                await self.existing_message.edit_text(
                    rich_message=rich_message,
                    reply_markup=reply_markup,
                )

        return self.existing_message
