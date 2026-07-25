from __future__ import annotations

import asyncio
from html import escape
from typing import TYPE_CHECKING

from aiogram import F, html
from aiogram.filters import CommandObject
from aiogram.fsm.state import State, StatesGroup

from raito import rt
from raito.plugins.commands import description, hidden
from raito.plugins.roles.roles import DEVELOPER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

    from raito.core.raito import Raito

router = rt.Router(name="raito.system.bash", priority=8, autoload=False)

DISABLED_MESSAGE = (
    "🚫 Dangerous commands are disabled.\n"
    "Set <code>Raito(enable_dangerous_commands=True)</code> to enable them."
)


class BashGroup(StatesGroup):
    expression = State()


async def _execute_expression(message: Message, text: str) -> None:
    process = await asyncio.create_subprocess_shell(text, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await process.communicate()
    await message.answer(text=html.pre(escape(stdout.decode())), parse_mode="HTML")


@router.message(RaitoCommand("bash", "sh"), DEVELOPER)
@description("Execute expression in commandline")
@hidden
async def bash_handler(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    raito: Raito,
) -> None:
    if not raito.enable_dangerous_commands:
        await message.answer(text=DISABLED_MESSAGE, parse_mode="HTML")
        return

    if not command.args:
        await message.answer(text="📦 Enter expression:")
        await state.set_state(BashGroup.expression)
        return

    await _execute_expression(message, command.args)


@router.message(BashGroup.expression, F.text, DEVELOPER)
async def execute_expression(message: Message, state: FSMContext, raito: Raito) -> None:
    await state.clear()

    if not raito.enable_dangerous_commands:
        await message.answer(text=DISABLED_MESSAGE, parse_mode="HTML")
        return

    if not message.text:
        await message.answer(text="⚠️ Expression cannot be empty")
        return

    await _execute_expression(message, message.text)
