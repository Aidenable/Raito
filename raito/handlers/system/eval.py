from __future__ import annotations

from typing import TYPE_CHECKING
import traceback
from html import escape

from aiogram import Router, html, F
from aiogram.fsm.state import State, StatesGroup

from raito.plugins.commands import description, hidden
from raito.plugins.roles.roles import DEVELOPER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext

    from raito.core.raito import Raito

router = Router(name="raito.system.eval")


class EvalGroup(StatesGroup):
    expression = State()


@router.message(RaitoCommand("eval"), DEVELOPER)
@description("Execute Python script")
@hidden
async def exec(message: Message, state: FSMContext) -> None:
    await message.answer(text="📦 Enter Python expression: ", parse_mode="HTML")
    await state.set_state(EvalGroup.expression)


@router.message(EvalGroup.expression, F.text, DEVELOPER)
async def execute_expression(message: Message, state: FSMContext, raito: Raito) -> None:
    try:
        result = eval(
            message.text, 
            {}, 
            {"_msg": message, "_user": message.from_user, "_raito": raito}
        )
        result = "no output" if result is None else str(result)
    except:
        result = traceback.format_exc()
    await state.clear()
    await message.answer(text=html.pre(escape(result)), parse_mode="HTML")
