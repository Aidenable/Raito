import re

from aiogram.filters import Filter
from aiogram.types import Message

PREFIX = ".rt"

__all__ = ("RaitoCommand",)


class RaitoCommand(Filter):
    """A filter for Raito bot commands.

    This class filters messages that match the Raito command format:
    ".rt <command> [arguments]"

    The filter matches commands exactly and optionally allows additional arguments.
    Commands are case-sensitive and must match the prefix ".rt" followed by
    one of the specified command strings.

    Example:

    .. code-block:: python

        @router.message(RaitoCommand("test"))
        async def test(message: Message):
            # Handles messages like:
            # ".rt test"
            # ".rt test foo bar 123"
            pass

    """

    def __init__(self, *commands: str) -> None:
        """Initialize the RaitoCommand filter.

        :param commands: One or more command strings to match
        :type commands: str
        :raises ValueError: If no commands are specified
        """
        if not commands:
            msg = "At least one command must be specified"
            raise ValueError(msg)

        pattern = rf"^{re.escape(PREFIX)} (?:{'|'.join(map(re.escape, commands))})(?: .+)?$"
        self._regex = re.compile(pattern)

    async def __call__(self, message: Message) -> bool:
        """Check if a message matches the command filter.

        :param message: The message to check
        :type message: Message
        :return: True if message matches command format, False otherwise
        :rtype: bool
        """
        if not message.text:
            return False
        return bool(self._regex.fullmatch(message.text.strip()))
