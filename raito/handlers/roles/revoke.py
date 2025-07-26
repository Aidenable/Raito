from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot, F, Router, html
from aiogram.fsm.state import State, StatesGroup

from raito.plugins.commands import description, hidden
from raito.plugins.commands.registration import register_bot_commands
from raito.plugins.roles.roles import ADMINISTRATOR, DEVELOPER, OWNER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

    from raito.core.raito import Raito

router = Router(name="raito.roles.revoke")


class RevokeRoleGroup(StatesGroup):
    """State group for revoking roles."""

    user_id = State()


@router.message(RaitoCommand("revoke"), DEVELOPER | OWNER | ADMINISTRATOR)
@description("Revokes a role from a user")
@hidden
async def revoke(message: Message, state: FSMContext) -> None:
    await message.answer("👤 Enter user ID:")
    await state.set_state(RevokeRoleGroup.user_id)


@router.message(
    RevokeRoleGroup.user_id,
    F.text and F.text.isdigit(),
    DEVELOPER | OWNER | ADMINISTRATOR,
)
async def revoke_role(message: Message, raito: Raito, state: FSMContext, bot: Bot) -> None:
    if not message.bot:
        await message.answer("🚫 Bot not found")
        return
    if not message.text or not message.text.isdigit():
        await message.answer("🚫 Invalid user ID")
        return
    if not message.from_user:
        await message.answer("🚫 Initiator not found")
        return
    await state.set_state()

    role_slug = await raito.role_manager.get_role(
        message.bot.id,
        int(message.text),
    )
    if not role_slug:
        await message.answer("⚠️ User does not have the role")
        return

    try:
        await raito.role_manager.revoke_role(
            message.bot.id,
            message.from_user.id,
            int(message.text),
        )
    except PermissionError:
        await message.answer("🚫 Permission denied")
        return

    role = raito.role_manager.get_role_data(role_slug)
    await message.answer(f"🛑 User revoked from {html.bold(role.label)}", parse_mode="HTML")

    handlers = []
    for loader in raito.router_manager.loaders.values():
        handlers.extend(loader.router.message.handlers)

    await register_bot_commands(raito.role_manager, bot, handlers, raito.locales)
