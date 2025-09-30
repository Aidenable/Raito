from aiogram.dispatcher.event.handler import CallbackType, FilterObject, HandlerObject
from aiogram.filters import Filter
from aiogram.types import TelegramObject


async def call_filters(
    event: TelegramObject,
    data: dict,
    *filters: CallbackType,
) -> bool:
    """Run a sequence of filters for a Telegram event.

    :param event: Telegram update object.
    :param data: Aiogram context dictionary.
    :param filters: Aiogram filters to apply.
    :return: True if all filters pass, False otherwise.
    :raises RuntimeError: If `handler` is missing from data.
    """
    handler_object: HandlerObject | None = data.get("handler")
    if handler_object is None:
        raise RuntimeError("Handler object not found")

    for f in filters:
        if isinstance(f, Filter):
            f.update_handler_flags(flags=handler_object.flags)

    for f in filters:
        obj = FilterObject(callback=f)
        if not await obj.call(event, **data):
            return False

    return True
