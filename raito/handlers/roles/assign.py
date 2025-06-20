from typing import TYPE_CHECKING, cast

from aiogram import F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from raito.plugins.roles import Role, roles
from raito.plugins.roles.data import ROLES_DATA
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from raito.core.raito import Raito

router = Router(name="raito.roles.assign")


class AssignRoleCallback(CallbackData, prefix="rt_assign_role"):
    """Callback data for assigning roles."""

    role_index: int


class AssignRoleGroup(StatesGroup):
    """State group for assigning roles."""

    user_id = State()


def roles_list_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, data in ROLES_DATA.items():
        builder.button(
            text=data.emoji + " " + data.name,
            callback_data=AssignRoleCallback(role_index=index),
        )

    return cast(InlineKeyboardMarkup, builder.adjust(2).as_markup())


@router.message(RaitoCommand("roles", "assign"))
@roles(Role.ADMINISTRATOR, Role.OWNER)
async def show_roles(message: Message) -> None:
    await message.answer("🎭 Select role to assign:", reply_markup=roles_list_markup())


@router.callback_query(AssignRoleCallback.filter())
@roles(Role.ADMINISTRATOR, Role.OWNER)
async def store_role(
    query: CallbackQuery,
    state: FSMContext,
    callback_data: AssignRoleCallback,
) -> None:
    if not query.bot:
        await query.answer("🚫 Bot not found", show_alert=True)
        return
    if not isinstance(query.message, Message):
        await query.answer("🚫 Invalid message", show_alert=True)
        return

    role = Role(callback_data.role_index)
    await state.update_data(rt_selected_role=role.value)
    await state.set_state(AssignRoleGroup.user_id)

    chat_id = query.message.chat.id
    await query.bot.send_message(
        chat_id=chat_id,
        text=f"{html.bold(role.label)}\n\n{html.blockquote(role.description)}",
        parse_mode="HTML",
    )
    await query.bot.send_message(chat_id=chat_id, text="👤 Enter user ID:")


@router.message(AssignRoleGroup.user_id, F.text and F.text.isdigit())
@roles(Role.ADMINISTRATOR, Role.OWNER)
async def assign_role(message: Message, raito: "Raito", state: FSMContext) -> None:
    data = await state.get_data()
    role_index = data.get("rt_selected_role")
    if role_index is None:
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

    role = Role(role_index)
    try:
        await raito.role_manager.assign_role(
            message.bot.id,
            message.from_user.id,
            int(message.text),
            role,
        )
    except PermissionError:
        await message.answer("🚫 Permission denied")
        return

    await message.answer(f"❇️ User assigned to {html.bold(role.label)}", parse_mode="HTML")
