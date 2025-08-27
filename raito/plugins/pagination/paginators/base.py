from __future__ import annotations

from typing import TYPE_CHECKING, cast
from uuid import uuid4

from aiogram.types import CallbackQuery, Update
from aiogram.utils.keyboard import InlineKeyboardBuilder

from raito.plugins.pagination.data import PaginationCallbackData
from raito.plugins.pagination.enums import PaginationMode
from raito.plugins.pagination.paginators.protocol import IPaginator
from raito.utils.configuration import RaitoConfiguration

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import (
        InlineKeyboardMarkup,
        Message,
        User,
    )

    from raito.core.raito import Raito

__all__ = ("BasePaginator",)


class BasePaginator(IPaginator):
    """Base paginator class."""

    def __init__(
        self,
        raito: Raito,
        name: str,
        chat_id: int,
        bot: Bot,
        from_user: User,
        *,
        existing_message: Message | None = None,
        current_page: int = 1,
        total_pages: int | None = None,
        limit: int = 20,
    ) -> None:
        """Initialize the Raito.

        :param raito: raito instance
        :type raito: Raito
        :param name: pagination name
        :type name: str
        :param chat_id: target chat id
        :type chat_id: int
        :param bot: bot instance
        :type bot: Bot
        :param from_user: user who triggered pagination
        :type from_user: User
        :param existing_message: existing message to edit
        :type existing_message: Message | None
        :param current_page: current page number
        :type current_page: int
        :param total_pages: total pages count, defaults None
        :type total_pages: int | None
        :param limit: items per page
        :type limit: int
        """
        self._validate_parameters(name, current_page, total_pages, limit)

        self.raito = raito
        self.name = name
        self.chat_id = chat_id
        self.bot = bot
        self.from_user = from_user
        self.existing_message = existing_message
        self._current_page = current_page
        self._total_pages = total_pages
        self._limit = limit

        self.configuration: RaitoConfiguration = self.raito.configuration

    def _validate_parameters(
        self, name: str, current_page: int, total_pages: int | None, limit: int
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
        if not name or len(name) > 32:
            raise ValueError("Name must be 1-32 characters long")

        if current_page < 1 or current_page >= 10**10:
            raise ValueError("Current page must be between 1 and 10^10")

        if total_pages is not None and (total_pages < current_page or total_pages >= 10**10):
            raise ValueError("Total pages must be >= current page and < 10^10")

        if limit < 1 or limit >= 10**5:
            raise ValueError("Limit must be between 1 and 10^5")

    def _create_callback_query(self) -> CallbackQuery:
        """Create callback query for pagination event.

        :return: callback query instance
        :rtype: CallbackQuery
        """
        return CallbackQuery(
            id=str(uuid4()),
            from_user=self.from_user,
            chat_instance=str(uuid4()),
            message=self.existing_message,
            data=PaginationCallbackData(
                mode=self.mode.value,
                name=self.name,
                current_page=self.current_page,
                total_pages=self.total_pages,
                limit=self.limit,
            ).pack(),
        )

    async def _invoke_callback(self) -> None:
        """Invoke pagination callback through dispatcher."""
        if not self.bot:
            raise ValueError("Bot instance not set")

        await self.raito.dispatcher.feed_update(
            bot=self.bot,
            update=Update(
                update_id=0,
                callback_query=self._create_callback_query(),
            ),
            paginator=self,
        )

    @property
    def current_page(self) -> int:
        """Get current page number."""
        return self._current_page

    @property
    def total_pages(self) -> int | None:
        """Get total pages count."""
        return self._total_pages

    @property
    def limit(self) -> int:
        """Get items per page limit."""
        return self._limit

    @property
    def mode(self) -> PaginationMode:
        """Get pagination mode.

        :raises NotImplementedError: must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement mode property")

    async def paginate(self) -> None:
        """Start pagination."""
        await self._invoke_callback()

    def get_previous_page(self) -> int:
        """Get previous page number with loop support.

        :return: previous page number
        :rtype: int
        """
        previous_page = self.current_page - 1

        if previous_page >= 1:
            return previous_page

        if self.configuration.pagination_style.loop_navigation and self.total_pages:
            return self.total_pages

        return self.current_page

    def get_next_page(self) -> int:
        """Get next page number with loop support.

        :return: next page number
        :rtype: int
        """
        next_page = self.current_page + 1

        if not self.total_pages:
            return next_page

        if next_page <= self.total_pages:
            return next_page

        if self.configuration.pagination_style.loop_navigation:
            return 1

        return self.current_page

    def _create_page_callback_data(self, page: int) -> PaginationCallbackData:
        """Create callback data for specific page.

        :param page: target page number
        :type page: int
        :return: callback data instance
        :rtype: PaginationCallbackData
        """
        return PaginationCallbackData(
            mode=self.mode.value,
            name=self.name,
            current_page=page,
            total_pages=self.total_pages,
            limit=self.limit,
        )

    def build_navigation(self) -> InlineKeyboardMarkup:
        """Build navigation inline keyboard.

        :return: navigation keyboard markup
        :rtype: InlineKeyboardMarkup
        """
        builder = InlineKeyboardBuilder()
        adjust = []

        builder.button(
            text=self.configuration.pagination_style.controls.previous,
            callback_data=self._create_page_callback_data(self.get_previous_page()),
        )
        builder.button(
            text=self.configuration.pagination_style.controls.next,
            callback_data=self._create_page_callback_data(self.get_next_page()),
        )
        adjust.append(2)

        if self.configuration.pagination_style.show_counter:
            counter_text = self.configuration.pagination_style.text_format.counter_template.format(
                current=self.current_page, total=self.total_pages or "∞"
            )
            builder.button(text=counter_text, callback_data="rt_p__counter")
            adjust.append(1)

        return cast(InlineKeyboardBuilder, builder.adjust(*adjust)).as_markup()

    @classmethod
    def calc_total_pages(cls, total_items: int, limit: int) -> int:
        """Calculate total pages from items count.

        :param total_items: total items count
        :type total_items: int
        :param limit: items per page
        :type limit: int
        :return: total pages count
        :rtype: int
        """
        if limit <= 0:
            raise ValueError("Limit must be greater than 0")

        return ((total_items or 1) + limit - 1) // limit
