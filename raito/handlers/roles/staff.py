from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router, html

from raito.plugins.commands import description, hidden
from raito.plugins.roles.roles import ADMINISTRATOR, DEVELOPER, OWNER
from raito.utils.ascii import AsciiTree, TreeNode
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message

    from raito.core.raito import Raito

router = Router(name="raito.roles.staff")


@router.message(RaitoCommand("staff"), DEVELOPER | OWNER | ADMINISTRATOR)
@description("Shows users with roles")
@hidden
async def list_staff(message: Message, raito: Raito, bot: Bot) -> None:
    root = TreeNode("staff", is_folder=True)

    for role in raito.role_manager.available_roles:
        role_node = root.add_child(role.label, prefix=role.emoji, is_folder=True)
        user_ids = await raito.role_manager.get_users(bot_id=bot.id, role=role.slug)

        for user_id in user_ids:
            role_node.add_child(html.code(str(user_id)))

    tree = AsciiTree(folder_icon="", sort=False).render(root)
    text = html.bold("Current staff:") + "\n\n" + tree
    await message.answer(text, parse_mode="HTML")
