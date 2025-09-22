from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from aiogram.filters import Command, CommandObject
from aiogram.filters.command import CommandException, CommandPatternType
from aiogram.utils.magic_filter import MagicFilter
from typing_extensions import override

PREFIX = ".rt "

__all__ = ("RaitoCommand",)


class RaitoCommand(Command):
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

    def __init__(
        self,
        *values: CommandPatternType,
        commands: Sequence[CommandPatternType] | CommandPatternType | None = None,
        ignore_case: bool = False,
        magic: MagicFilter | None = None,
    ) -> None:
        """Initialize the RaitoCommand filter.

        :param commands: One or more command strings to match
        :param ignore_case: Ignore case (Does not work with regexp, use flags instead)
        :param magic: Validate command object via Magic filter after all checks done
        :raises ValueError: If no commands are specified
        """
        super().__init__(
            *values,
            commands=commands,
            ignore_case=ignore_case,
            ignore_mention=True,
            magic=magic,
        )

        self.prefix = PREFIX
        pattern = (
            rf"^{re.escape(self.prefix)} (?:{'|'.join(map(re.escape, self.commands))})(?: .+)?$"
        )
        self._regex = re.compile(pattern)

    @override
    def extract_command(self, text: str) -> CommandObject:
        # First step: separate command with arguments
        # ".rt command arg1 arg2" -> ".rt", "command", ["arg1 arg2"]
        try:
            prefix, command, *args = text.split(maxsplit=2)
        except ValueError as exc:
            msg = "Not enough values to unpack"
            raise CommandException(msg) from exc

        return CommandObject(prefix=prefix + " ", command=command, args=args[0] if args else None)

    @override
    def update_handler_flags(self, flags: dict[str, Any]) -> None:
        super().update_handler_flags(flags)
        flags["raito__command"] = True
