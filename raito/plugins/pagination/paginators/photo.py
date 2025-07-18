from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.client.default import Default
from aiogram.types import InputMediaPhoto

from raito.plugins.pagination.enums import PaginationMode

from .base import BasePaginator

if TYPE_CHECKING:
    from aiogram.types import (
        InlineKeyboardMarkup,
        InputFileUnion,
        Message,
        MessageEntity,
        ReplyParameters,
    )


__all__ = ("PhotoPaginator",)


class PhotoPaginator(BasePaginator):
    """Photo paginator."""

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
        if limit > 1024:
            raise ValueError("limit must be less than or equal to 1024")

        return super()._validate_parameters(
            name=name,
            current_page=current_page,
            total_pages=total_pages,
            limit=limit,
        )

    @property
    def mode(self) -> PaginationMode:
        """Get text pagination mode.

        :return: pagination mode
        :rtype: PaginationMode
        """
        return PaginationMode.PHOTO

    async def answer(
        self,
        photo: InputFileUnion,
        caption: str | None = None,
        parse_mode: str | Default | None = None,
        caption_entities: list[MessageEntity] | None = None,
        show_caption_above_media: bool | Default | None = None,
        has_spoiler: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | Default | None = None,
        allow_paid_broadcast: bool | None = None,
        message_effect_id: str | None = None,
        reply_parameters: ReplyParameters | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
        allow_sending_without_reply: bool | None = None,
        reply_to_message_id: int | None = None,
    ) -> Message:
        """Send or edit paginated message.

        :param photo: photo file
        :type photo: InputFileUnion
        :param caption: message text
        :type caption: str
        :param parse_mode: text parse mode
        :type parse_mode: str | Default | None
        :param caption_entities: message entities
        :type caption_entities: list[MessageEntity] | None
        :param show_caption_above_media: show caption above media
        :type show_caption_above_media: bool | None
        :param has_spoiler: has spoiler
        :type has_spoiler: bool | None
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
        :param reply_to_message_id: reply to message id
        :type reply_to_message_id: int | None
        :return: paginated message
        :rtype: Message
        :raises RuntimeError: if bot instance not set
        """
        if not self.bot:
            raise RuntimeError("Bot not set via PaginatorMiddleware")

        parse_mode = parse_mode or Default("parse_mode")
        show_caption_above_media = show_caption_above_media or Default("show_caption_above_media")
        protect_content = protect_content or Default("protect_content")

        reply_markup = reply_markup or self.build_navigation()

        if self.existing_message is None:
            self.existing_message = await self.bot.send_photo(
                chat_id=self.chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                show_caption_above_media=show_caption_above_media,
                has_spoiler=has_spoiler,
                disable_notification=disable_notification,
                protect_content=protect_content,
                allow_paid_broadcast=allow_paid_broadcast,
                message_effect_id=message_effect_id,
                reply_parameters=reply_parameters,
                reply_markup=reply_markup,
                allow_sending_without_reply=allow_sending_without_reply,
                reply_to_message_id=reply_to_message_id,
            )
        else:
            await self.existing_message.edit_media(
                media=InputMediaPhoto(media=photo, caption=caption, reply_markup=reply_markup),
                caption=caption,
                reply_markup=reply_markup,
            )

        return self.existing_message
