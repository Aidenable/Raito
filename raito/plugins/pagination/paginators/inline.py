from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.client.default import Default
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from raito.plugins.pagination.enums import PaginationMode
from raito.utils.errors import SuppressNotModifiedError

from .base import BasePaginator

if TYPE_CHECKING:
    from aiogram.types import (
        InlineKeyboardButton,
        LinkPreviewOptions,
        Message,
        MessageEntity,
        ReplyParameters,
    )


__all__ = ("InlinePaginator",)


class InlinePaginator(BasePaginator):
    """Inline keyboard paginator."""

    def _validate_parameters(
        self,
        name: str,
        current_page: int,
        total_pages: int | None,
        limit: int,
    ) -> None:
        """Validate paginator parameters.

        :param name: pagination name
        :type name: str
        :param current_page: current page number
        :type current_page: int
        :param total_pages: total pages count
        :type total_pages: int | None
        :param limit: items per page
        :type limit: int
        :raises ValueError: if parameters are invalid
        """
        if limit > 90:
            raise ValueError("limit must be less than or equal to 90")

        return super()._validate_parameters(
            name=name,
            current_page=current_page,
            total_pages=total_pages,
            limit=limit,
        )

    @property
    def mode(self) -> PaginationMode:
        """Get inline pagination mode.

        :return: pagination mode
        :rtype: PaginationMode
        """
        return PaginationMode.INLINE

    def _get_content_builder(
        self,
        buttons: list[InlineKeyboardButton] | InlineKeyboardMarkup | None = None,
    ) -> InlineKeyboardBuilder:
        """Build content keyboard from buttons.

        :param buttons: content buttons or markup
        :type buttons: list[InlineKeyboardButton] | InlineKeyboardMarkup | None
        :return: keyboard builder with content
        :rtype: InlineKeyboardBuilder
        """
        builder = InlineKeyboardBuilder()

        if isinstance(buttons, list):
            builder.row(*buttons, width=1)
        elif isinstance(buttons, InlineKeyboardMarkup):
            content_builder = InlineKeyboardBuilder.from_markup(buttons)
            builder.attach(content_builder)

        return builder

    def _get_reply_markup(
        self,
        reply_markup: InlineKeyboardMarkup | None = None,
        buttons: list[InlineKeyboardButton] | InlineKeyboardMarkup | None = None,
    ) -> InlineKeyboardMarkup:
        """Build reply markup with content and navigation.

        :param buttons: content buttons or markup
        :type buttons: list[InlineKeyboardButton] | InlineKeyboardMarkup | None
        :return: complete keyboard markup
        :rtype: InlineKeyboardMarkup
        """
        builder = InlineKeyboardBuilder()

        if isinstance(buttons, list):
            builder.row(*buttons, width=1)
        elif isinstance(buttons, InlineKeyboardMarkup):
            builder.attach(builder.from_markup(buttons))

        if reply_markup is not None:
            builder.attach(builder.from_markup(reply_markup))
        else:
            builder.attach(builder.from_markup(self.build_navigation()))

        return builder.as_markup()

    async def answer(
        self,
        text: str,
        buttons: list[InlineKeyboardButton] | InlineKeyboardMarkup | None = None,
        parse_mode: str | Default | None = None,
        entities: list[MessageEntity] | None = None,
        link_preview_options: LinkPreviewOptions | Default | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | Default | None = None,
        allow_paid_broadcast: bool | None = None,
        message_effect_id: str | None = None,
        reply_parameters: ReplyParameters | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
        allow_sending_without_reply: bool | None = None,
        disable_web_page_preview: bool | Default | None = None,
        reply_to_message_id: int | None = None,
    ) -> Message:
        """Send or edit paginated message.

        :param text: message text
        :type text: str
        :param buttons: content buttons
        :type buttons: list[list[InlineKeyboardButton]]
        :param parse_mode: text parse mode
        :type parse_mode: str | Default | None
        :param entities: message entities
        :type entities: list[MessageEntity] | None
        :param link_preview_options: link preview settings
        :type link_preview_options: LinkPreviewOptions | Default | None
        :param disable_notification: disable notification
        :type disable_notification: bool | None
        :param protect_content: protect content
        :type protect_content: bool | Default | None
        :param allow_paid_broadcast: allow paid broadcast
        :type allow_paid_broadcast: bool | None
        :param message_effect_id: message effect id
        :type message_effect_id: int | None
        :param reply_parameters: reply parameters
        :type reply_parameters: ReplyParameters | None
        :param reply_markup: custom reply markup
        :type reply_markup: InlineKeyboardMarkup | None
        :param allow_sending_without_reply: allow sending without reply
        :type allow_sending_without_reply: bool | None
        :param disable_web_page_preview: disable web page preview
        :type disable_web_page_preview: bool | Default | None
        :param reply_to_message_id: reply to message id
        :type reply_to_message_id: int | None
        :return: paginated message
        :rtype: Message
        :raises RuntimeError: if bot instance not set
        """
        if not self.bot:
            raise RuntimeError("Bot not set via PaginatorMiddleware")

        parse_mode = parse_mode or Default("parse_mode")
        link_preview_options = link_preview_options or Default("link_preview")
        protect_content = protect_content or Default("protect_content")
        disable_web_page_preview = disable_web_page_preview or Default("link_preview_is_disabled")

        reply_markup = (
            reply_markup
            if reply_markup is not None and buttons is None
            else self._get_reply_markup(reply_markup, buttons)
        )

        if self.existing_message is None:
            self.existing_message = await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                link_preview_options=link_preview_options,
                disable_notification=disable_notification,
                protect_content=protect_content,
                allow_paid_broadcast=allow_paid_broadcast,
                message_effect_id=message_effect_id,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id,
            )
        elif text != self.existing_message.text:
            with SuppressNotModifiedError():
                await self.existing_message.edit_text(
                    text=text,
                    parse_mode=parse_mode,
                    entities=entities,
                    link_preview_options=link_preview_options,
                    reply_markup=reply_markup,
                    disable_web_page_preview=disable_web_page_preview,
                )
        else:
            with SuppressNotModifiedError():
                await self.existing_message.edit_reply_markup(reply_markup=reply_markup)

        return self.existing_message
