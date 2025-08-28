from aiogram import Router, filters, html
from aiogram.types import Message

from raito import rt
from raito.plugins.roles.roles import DEVELOPER

router = Router(name="eval")


@router.message(filters.Command("eval"), DEVELOPER)
@rt.description("Execute a Python expression and return the result")
async def eval_handler(message: Message, command: filters.CommandObject | None = None) -> None:
    if not command or not command.args:
        await message.answer("⚠️ No expression provided.")
        return

    try:
        result = eval(command.args, {"__builtins__": {}}, {})
    except Exception as e:
        result = f"[error] {type(e).__name__}: {e}"

    response = "\n".join(
        (
            html.italic("• Code:"),
            html.pre_language(command.args, language="python"),
            "",
            html.italic("• Result:"),
            html.pre(str(result)),
        )
    )

    await message.answer(response)
