from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from aiogram import html

from raito import rt
from raito.plugins.commands import description, hidden
from raito.plugins.roles import DEVELOPER
from raito.utils.ascii import AsciiTree, TreeNode
from raito.utils.configuration import RouterListStyle
from raito.utils.const import ROOT_DIR
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.types import Message

    from raito.core.raito import Raito
    from raito.core.routers.loader import RouterLoader

router = rt.Router(name="raito.management.list", priority=4)


class Emojis(NamedTuple):
    """Emojis for router status."""

    enabled: str
    restarting: str
    disabled: str
    not_found: str


@router.message(RaitoCommand("routers"), DEVELOPER)
@description("Lists all routers")
@hidden
async def list_routers(message: Message, raito: Raito) -> None:
    match raito.configuration.router_list_style:
        case RouterListStyle.CIRCLES:
            emojis = Emojis("🟢", "🟡", "🔴", "⚪")
        case RouterListStyle.DIAMONDS:
            emojis = Emojis("🔹", "🔸", "🔸", "🔸")
        case RouterListStyle.DIAMONDS_REVERSED:
            emojis = Emojis("🔸", "🔹", "🔹", "🔹")
        case _:
            emojis = Emojis("🟩", "🟨", "🟥", "⬜")

    def extract_loader_path(loader: RouterLoader) -> str:
        return (
            loader.path.as_posix()
            .replace(ROOT_DIR.parent.as_posix(), "")
            .replace(".py", "")
            .strip("/")
        )

    paths = {
        extract_loader_path(loader): loader for loader in raito.router_manager.loaders.values()
    }

    def get_status_icon(path: str) -> str:
        loader = paths.get(path)
        if loader and loader.is_restarting:
            return emojis.restarting
        if loader and loader.is_loaded:
            return emojis.enabled
        return emojis.disabled

    root = TreeNode("routers", is_folder=True)
    for path in paths:
        parts = path.split("/")
        current = root
        for i, part in enumerate(parts):
            full_path = "/".join(parts[: i + 1])
            is_folder = i != len(parts) - 1
            icon = get_status_icon(full_path) if not is_folder else ""
            current = current.add_child(part, prefix=icon, is_folder=is_folder)

    tree = AsciiTree().render(root)
    text = (
        html.bold("Here is your routers:")
        + "\n\n"
        + tree
        + "\n\n"
        + html.pre_language((f"{emojis[0]} — Enabled\n{emojis[2]} — Disabled\n"), "Specification")
    )

    await message.answer(text, parse_mode="HTML")
