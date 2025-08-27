from typing import TypeVar

from aiogram.exceptions import TelegramBadRequest

T = TypeVar("T")


class SuppressNotModifiedError:
    """
    Context manager that suppresses the ``TelegramBadRequest`` exception
    with the message ``Bad Request: message is not modified``.

    This is useful when editing a Telegram message and the new content
    is identical to the existing one, which would otherwise raise
    an error from the Telegram API.

    Example:

        .. code-block:: python

            from raito.utils.errors import SuppressNotModifiedError

            with SuppressNotModifiedError():
                await message.edit_text("same text")

    :param ignore_message: The exact error message to match.
                           If this message is found in the raised
                           ``TelegramBadRequest``, the exception is suppressed.
                           Defaults to ``"Bad Request: message is not modified"``.
    :type ignore_message: str
    """

    def __init__(self, ignore_message: str = "Bad Request: message is not modified") -> None:
        """Initialize the context manager.

        :param ignore_message: Error message string to match against.
        """
        self.ignore_message = ignore_message

    def __enter__(self: T) -> T:
        """Enter the runtime context related to this object.

        :return: The context manager instance itself.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        _: object | None,
    ) -> bool:
        """Exit the runtime context and suppress the exception if it matches.

        :param exc_type: The exception type (if any).
        :param exc_val: The exception instance (if any).
        :param _: The traceback object (unused).
        :return: True if the exception should be suppressed, False otherwise.
        :rtype: bool
        """
        return (
            exc_type is TelegramBadRequest
            and exc_val is not None
            and self.ignore_message in str(exc_val)
        )
