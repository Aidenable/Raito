from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram import html

if TYPE_CHECKING:
    from aiogram.filters.command import CommandObject

EXAMPLE_VALUES = {
    bool: "yes",
    str: "word",
    int: "10",
    float: "3.14",
}


def get_command_help(
    command: CommandObject,
    params: dict[str, type[Any]],
) -> str:
    """Get the help message of a command."""
    cmd = command.prefix + command.command

    signature = cmd
    example = cmd
    for param, value_type in params.items():
        signature += f" [{param}]"
        example += " " + EXAMPLE_VALUES[value_type]

    return (
        html.italic("— Signature:\n")
        + html.code(signature)
        + html.italic("\n\n— Example: ")
        + html.blockquote(example)
    )
