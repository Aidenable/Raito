from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot, F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from raito.plugins.commands import description
from raito.plugins.commands.flags import hidden
from raito.plugins.commands.registration import register_bot_commands
from raito.plugins.keyboards import dynamic
from raito.plugins.roles.data import RoleData
from raito.plugins.roles.roles import ADMINISTRATOR, DEVELOPER, OWNER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery

    from raito.core.raito import Raito

router = Router(name="raito.roles.assign")


class AssignRoleCallback(CallbackData, prefix="rt_assign_role"):  # type: ignore[call-arg]
    """Callback data for assigning roles."""

    role_slug: str


class AssignRoleGroup(StatesGroup):
    """State group for assigning roles."""

    user_id = State()


@dynamic(2)
def roles_list_markup(builder: InlineKeyboardBuilder, roles: list[RoleData]) -> None:
    for role in roles:
        builder.button(
            text=role.emoji + " " + role.name,
            callback_data=AssignRoleCallback(role_slug=role.slug),
        )


@router.message(RaitoCommand("roles", "assign"), DEVELOPER | OWNER | ADMINISTRATOR)
@description("Assigns a role to a user")
@hidden
async def show_roles(message: Message, raito: Raito) -> None:
    await message.answer(
        "🎭 Select role to assign:",
        reply_markup=roles_list_markup(raito.role_manager.available_roles),
    )


@router.callback_query(AssignRoleCallback.filter(), DEVELOPER | OWNER | ADMINISTRATOR)
async def store_role(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: AssignRoleCallback,
    raito: Raito,
) -> None:
    if not query.bot:
        await query.answer("🚫 Bot not found", show_alert=True)
        return
    if not isinstance(query.message, Message):
        await query.answer("🚫 Invalid message", show_alert=True)
        return

    role = raito.role_manager.get_role_data(callback_data.role_slug)
    await state.update_data(rt_selected_role=role.slug)
    await state.set_state(AssignRoleGroup.user_id)

    chat_id = query.message.chat.id
    await query.bot.send_message(
        chat_id=chat_id,
        text=f"{html.bold(role.label)}\n\n{html.blockquote(role.description)}",
        parse_mode="HTML",
    )
    await query.bot.send_message(chat_id=chat_id, text="👤 Enter user ID:")


@router.message(
    AssignRoleGroup.user_id,
    F.text and F.text.isdigit(),
    DEVELOPER | OWNER | ADMINISTRATOR,
)
async def assign_role(message: Message, raito: Raito, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    role_slug = data.get("rt_selected_role")
    if role_slug is None:
        await message.answer("🚫 Role not selected")
        return
    if not message.from_user:
        await message.answer("🚫 User not found")
        return
    if not message.text or not message.text.isdigit():
        await message.answer("🚫 Invalid user ID")
        return
    if not message.bot:
        await message.answer("🚫 Bot instance not found")
        return

    await state.update_data(rt_selected_role=None)
    await state.set_state()

    role = raito.role_manager.get_role_data(role_slug)
    try:
        await raito.role_manager.assign_role(
            message.bot.id,
            message.from_user.id,
            int(message.text),
            role.slug,
        )
    except PermissionError:
        await message.answer("🚫 Permission denied")
        return

    await message.answer(f"❇️ User assigned to {html.bold(role.label)}", parse_mode="HTML")

    handlers = []
    for loader in raito.router_manager.loaders.values():
        handlers.extend(loader.router.message.handlers)

    await register_bot_commands(raito.role_manager, bot, handlers, raito.locales)
