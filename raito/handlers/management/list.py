from typing import TYPE_CHECKING, NamedTuple

from aiogram import Router, html
from aiogram.types import Message

from raito.plugins.roles import Role, roles
from raito.utils.ascii.tree import AsciiTree, dot_paths_to_tree
from raito.utils.configuration import Configuration
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from raito.core.raito import Raito

router = Router(name="raito.management.list")


class Emojis(NamedTuple):
    """Emojis for router status."""

    enabled: str
    restarting: str
    disabled: str
    not_found: str


@router.message(RaitoCommand("routers"))
@roles(Role.DEVELOPER)
async def list_routers(message: Message, raito: "Raito") -> None:
    match raito.configuration.router_list_style:
        case Configuration.RouterListStyle.CIRCLES:
            emojis = Emojis("🟢", "🟡", "🔴", "⚪")
        case Configuration.RouterListStyle.RHOMBUSES:
            emojis = Emojis("🔹", "🔸", "🔸", "🔸")
        case Configuration.RouterListStyle.RHOMBUSES_REVERSED:
            emojis = Emojis("🔸", "🔹", "🔹", "🔹")
        case _:
            emojis = Emojis("🟩", "🟨", "🟥", "⬜")

    def get_router_emoji(path: str) -> str:
        if path in raito.router_manager.loaders:
            loader = raito.router_manager.loaders[path]
            if loader.is_restarting:
                return emojis.restarting
            if loader.is_loaded:
                return emojis.enabled
        return emojis.disabled

    paths = list(raito.router_manager.loaders.keys())
    tree_root = dot_paths_to_tree(paths, prefix_callback=get_router_emoji)
    tree = AsciiTree().render(tree_root)

    text = (
        html.bold("Here is your routers:")
        + "\n\n"
        + tree
        + "\n\n"
        + html.pre_language((f"{emojis[0]} — Enabled\n{emojis[2]} — Disabled\n"), "Specification")
    )

    await message.answer(text, parse_mode="HTML")
