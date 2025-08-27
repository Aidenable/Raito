from aiogram.filters.callback_data import CallbackData

__all__ = ("PaginationCallbackData",)

_PREFIX = "rt_p"


class PaginationCallbackData(CallbackData, prefix=_PREFIX):  # type: ignore[call-arg]
    """Callback data for inline navigation buttons.

    :param mode: pagination mode
    :type mode: int
    :param name: paginator name
    :type name: str
    :param current_page: current page number
    :type current_page: int
    :param total_pages: total pages count or None
    :type total_pages: int | None
    :param limit: items per page
    :type limit: int
    """

    mode: int
    name: str
    current_page: int
    total_pages: int | None
    limit: int
