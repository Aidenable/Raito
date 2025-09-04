from __future__ import annotations

import traceback
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

    from raito.core.raito import Raito

router = Router(name="raito.system.eval")


class EvalGroup(StatesGroup):
    expression = State()


@router.message(RaitoCommand("eval"), DEVELOPER)
@description("Execute Python script")
@hidden
async def exec(message: Message, state: FSMContext) -> None:
    await message.answer(text="📦 Enter Python expression: ")
    await state.set_state(EvalGroup.expression)


@router.message(EvalGroup.expression, F.text, DEVELOPER)
async def execute_expression(message: Message, state: FSMContext, raito: Raito) -> None:
    await state.clear()

    if not message.text:
        await message.answer(text="⚠️ Expression cannot be empty")
        return

    try:
        result = eval(
            message.text,
            {},
            {"_msg": message, "_user": message.from_user, "_raito": raito},
        )
        result = "no output" if result is None else str(result)
    except Exception:  # noqa: BLE001
        result = traceback.format_exc()

    await message.answer(text=html.pre(escape(result)), parse_mode="HTML")
