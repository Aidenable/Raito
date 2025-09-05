from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING, Any

from aiogram import F, Router, html
from aiogram.filters import CommandObject
from aiogram.fsm.state import State, StatesGroup

from raito.plugins.commands import description, hidden
from raito.plugins.roles import DEVELOPER
from raito.utils.filters import RaitoCommand
from raito.utils.helpers.code_evaluator import CodeEvaluator

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

router = Router(name="raito.system.eval")
code_evaluator = CodeEvaluator()


class EvalGroup(StatesGroup):
    expression = State()


async def _execute_code(message: Message, code: str, data: dict[str, Any]) -> None:
    data = {"_" + k: v for k, v in data.items()}
    data["_msg"] = message
    data["_user"] = message.from_user

    evaluation_data = await code_evaluator.evaluate(code, data)
    pre_blocks = []

    if evaluation_data.stdout:
        pre_blocks.append(evaluation_data.stdout[:1000])

    if evaluation_data.error:
        pre_blocks.append(evaluation_data.error[:3000])
    elif evaluation_data.result is not None:
        pre_blocks.append(evaluation_data.result[:3000])
    else:
        pre_blocks.append("no output")

    text = "\n\n".join([html.pre(escape(i)) for i in pre_blocks])
    await message.answer(text=text, parse_mode="HTML")


@router.message(RaitoCommand("eval", "py", "py3", "python", "exec"), DEVELOPER)
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
    await _execute_code(message, command.args, data)


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
    await _execute_code(message, message.text, data)
