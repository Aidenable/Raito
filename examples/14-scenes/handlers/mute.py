from aiogram import F, filters
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from raito import Router
from raito.plugins.scenes import Scene, SceneData

router = Router(name="mute")


class MuteData(SceneData):
    username: str | None = None
    duration: int | None = None


class MuteStates(StatesGroup):
    username = State()
    duration = State()
    confirm = State()


mute = router.scene(MuteStates, data=MuteData)


@mute.on_message.enter(filters.Command("mute"))
async def start(message: Message, scene: Scene[MuteData]) -> None:
    await message.answer("Enter username:")
    await scene.next()


# Declared before the broad F.text steps below, so /cancel always wins the race
# regardless of which step the user is on — see "Handling an unrelated command".
@mute.on_message.any(filters.Command("cancel"))
async def cancel_anywhere(message: Message, scene: Scene[MuteData]) -> None:
    await message.answer("Cancelled")
    await scene.cancel()


@mute.on_message(MuteStates.username, F.text)
async def username(message: Message, scene: Scene[MuteData]) -> None:
    value = message.text or ""
    if not value.startswith("@"):
        await message.answer("⚠️ Enter an @username")
        return await scene.retry()

    scene.data.username = value
    await message.answer("Enter duration in minutes:")
    await scene.next()


@mute.on_message(MuteStates.duration, F.text)
async def duration(message: Message, scene: Scene[MuteData]) -> None:
    value = message.text or ""
    if not value.isdigit() or int(value) <= 0:
        await message.answer("⚠️ Enter a positive whole number")
        return await scene.retry()

    scene.data.duration = int(value)

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Confirm", callback_data="confirm")
    keyboard.button(text="❌ Cancel", callback_data="cancel")
    await message.answer(
        f"Mute {scene.data.username} for {scene.data.duration} minutes?",
        reply_markup=keyboard.as_markup(),
    )
    await scene.next()


@mute.on_callback_query(MuteStates.confirm, F.data == "confirm")
async def confirm(callback_query: CallbackQuery, scene: Scene[MuteData]) -> None:
    await callback_query.answer()
    if isinstance(callback_query.message, Message):
        await callback_query.message.edit_text(
            f"✅ {scene.data.username} will be muted for {scene.data.duration} minutes",
        )
    await scene.finish()


@mute.on_callback_query(MuteStates.confirm, F.data == "cancel")
async def decline(callback_query: CallbackQuery, scene: Scene[MuteData]) -> None:
    await callback_query.answer()
    if isinstance(callback_query.message, Message):
        await callback_query.message.edit_text("Cancelled")
    await scene.cancel()
