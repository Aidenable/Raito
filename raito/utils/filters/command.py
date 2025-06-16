import re

from aiogram.filters import Filter
from aiogram.types import Message

PREFIX = ".rt"


class RaitoCommand(Filter):  # type: ignore[misc]
    def __init__(self, *commands: str) -> None:
        if not commands:
            raise ValueError("At least one command must be specified")

        pattern = rf"^{re.escape(PREFIX)} (?:{'|'.join(map(re.escape, commands))})(?: .+)?$"
        self._regex = re.compile(pattern)

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return bool(self._regex.fullmatch(message.text.strip()))
