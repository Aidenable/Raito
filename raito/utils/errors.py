from typing import TypeVar

from aiogram.exceptions import TelegramBadRequest

T = TypeVar("T")


class SuppressNotModifiedError:
    def __init__(self, ignore_message: str = "Bad Request: message is not modified") -> None:
        self.ignore_message = ignore_message

    def __enter__(self: T) -> T:
        return self

    def __exit__(
        self,
        exc_type: BaseException | None,
        exc_val: BaseException | None,
        _: object | None,
    ) -> bool:
        return (
            exc_type is TelegramBadRequest
            and exc_val is not None
            and self.ignore_message in str(exc_val)
        )
