from datetime import datetime

from aiogram import Router, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from raito import rt

router = Router(name="start")


class Form(StatesGroup):
    message = State()


@router.message(filters.CommandStart())
@rt.description("Start command")
async def start(message: Message, state: FSMContext) -> None:
    await state.update_data(sent_at=message.date.timestamp())
    await state.set_state(Form.message)
    await message.answer("Send me a message")


@router.message(Form.message)
async def new_message(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    previous_ts = data.get("sent_at")
    current_ts = message.date.timestamp()

    if previous_ts is None:
        await message.answer("⚠️ Failed to determine the previous message time.")
        return

    previous_time = datetime.fromtimestamp(previous_ts)
    current_time = datetime.fromtimestamp(current_ts)
    diff = int(current_ts - previous_ts)

    await message.answer(
        "🕒 <b>Time between messages:</b>\n"
        f"<i>• Previous:</i> {previous_time:%H:%M:%S}\n"
        f"<i>• Current:</i> {current_time:%H:%M:%S}\n"
        "\n"
        f"⏱️ Difference: <b>{diff}s</b>"
    )
