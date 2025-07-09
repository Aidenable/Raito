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
    command_object: CommandObject,
    params: dict[str, type[Any]],
    description: str | None = None,
) -> str:
    """Get the help message of a command."""
    cmd = command_object.prefix + command_object.command

    signature = cmd
    example = cmd
    for param, value_type in params.items():
        signature += f" [{param}]"
        example += " " + EXAMPLE_VALUES[value_type]

    description = "\n" + html.expandable_blockquote(html.italic(description)) if description else ""

    return (
        html.bold(cmd)
        + description
        + html.italic("\n\n— Signature:\n")
        + html.code(signature)
        + html.italic("\n\n— Example:\n")
        + html.code(example)
    )
