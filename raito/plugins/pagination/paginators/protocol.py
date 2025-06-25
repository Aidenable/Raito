from typing import TYPE_CHECKING, Protocol

from raito.plugins.pagination.enums import PaginationMode

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

__all__ = ("IPaginator",)


class IPaginator(Protocol):
    """Protocol for paginator implementations.

    Defines the interface that all paginator classes must implement.
    """

    @property
    def current_page(self) -> int:
        """Get current page number.

        :return: current page number
        :rtype: int
        """
        ...

    @property
    def total_pages(self) -> int | None:
        """Get total pages count.

        :return: total pages or None
        :rtype: int | None
        """
        ...

    @property
    def limit(self) -> int:
        """Get items per page limit.

        :return: items per page
        :rtype: int
        """
        ...

    @property
    def mode(self) -> "PaginationMode":
        """Get pagination mode.

        :return: pagination mode
        :rtype: PaginationMode
        """
        ...

    async def paginate(self) -> None:
        """Start pagination."""
        ...

    def get_previous_page(self) -> int:
        """Get previous page number.

        :return: previous page number
        :rtype: int
        """
        ...

    def get_next_page(self) -> int:
        """Get next page number.

        :return: next page number
        :rtype: int
        """
        ...

    def build_navigation(self) -> "InlineKeyboardMarkup":
        """Build navigation keyboard.

        :return: navigation keyboard markup
        :rtype: InlineKeyboardMarkup
        """
        ...

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
        ...
