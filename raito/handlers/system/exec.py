from __future__ import annotations

import os
from html import escape
from typing import TYPE_CHECKING

from aiogram import F, Router, html
from aiogram.fsm.state import State, StatesGroup

from raito.plugins.commands import description, hidden
from raito.plugins.roles.roles import DEVELOPER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

router = Router(name="raito.system.exec")


class ExecGroup(StatesGroup):
    expression = State()


@router.message(RaitoCommand("exec"), DEVELOPER)
@description("Execute expression in commandline")
@hidden
async def exec(message: Message, state: FSMContext) -> None:
    await message.answer(text="📦 Enter expression: ", parse_mode="HTML")
    await state.set_state(ExecGroup.expression)


@router.message(ExecGroup.expression, F.text, DEVELOPER)
async def execute_expression(message: Message, state: FSMContext) -> None:
    result = os.popen(message.text).read()
    await state.clear()
    await message.answer(text=html.pre(escape(result)), parse_mode="HTML")
