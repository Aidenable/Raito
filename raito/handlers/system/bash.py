from __future__ import annotations

import os
from html import escape
from typing import TYPE_CHECKING

from aiogram import F, Router, html
from aiogram.filters import CommandObject
from aiogram.fsm.state import State, StatesGroup

from raito.plugins.commands import description, hidden
from raito.plugins.roles.roles import DEVELOPER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

router = Router(name="raito.system.bash")


class BashGroup(StatesGroup):
    expression = State()


async def _execute_expression(message: Message, text: str) -> None:
    result = os.popen(text).read()
    await message.answer(text=html.pre(escape(result)), parse_mode="HTML")


@router.message(RaitoCommand("bash", "sh"), DEVELOPER)
@description("Execute expression in commandline")
@hidden
async def bash_handler(message: Message, state: FSMContext, command: CommandObject) -> None:
    if not command.args:
        await message.answer(text="📦 Enter expression:")
        await state.set_state(BashGroup.expression)
        return

    await _execute_expression(message, command.args)


@router.message(BashGroup.expression, F.text, DEVELOPER)
async def execute_expression(message: Message, state: FSMContext) -> None:
    await state.clear()

    if not message.text:
        await message.answer(text="⚠️ Expression cannot be empty")
        return

    await _execute_expression(message, message.text)
