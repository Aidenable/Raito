from __future__ import annotations

import traceback
from html import escape
from typing import TYPE_CHECKING, Any

from aiogram import F, Router, html
from aiogram.filters import CommandObject
from aiogram.fsm.state import State, StatesGroup

from raito.plugins.commands import description, hidden
from raito.plugins.roles import DEVELOPER
from raito.utils.filters import RaitoCommand

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

router = Router(name="raito.system.eval")


class EvalGroup(StatesGroup):
    expression = State()


async def _eval_code(message: Message, code: str, data: dict[str, Any]) -> None:
    data = {"_" + k: v for k, v in data.items()}
    data["_msg"] = message
    data["_user"] = message.from_user

    try:
        result = eval(code, {}, data)
        result = "no output" if result is None else str(result)
    except Exception:  # noqa: BLE001
        result = traceback.format_exc()

    await message.answer(text=html.pre(escape(result)), parse_mode="HTML")


@router.message(RaitoCommand("eval"), DEVELOPER)
@description("Execute Python script")
@hidden
async def eval_handler(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    **data: Any,  # noqa: ANN401
) -> None:
    if not command.args:
        await message.answer(text="📦 Enter Python expression:")
        await state.set_state(EvalGroup.expression)
        return

    data["message"] = message
    data["state"] = state
    data["command"] = command
    await _eval_code(message, command.args, data)


@router.message(EvalGroup.expression, F.text, DEVELOPER)
async def eval_process(
    message: Message,
    state: FSMContext,
    **data: Any,  # noqa: ANN401
) -> None:
    await state.clear()

    if not message.text:
        await message.answer(text="⚠️ Expression cannot be empty")
        return

    data["message"] = message
    data["state"] = state
    await _eval_code(message, message.text, data)
