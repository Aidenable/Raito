from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from raito import rt
from raito.plugins.pagination import InlinePaginator

router = Router(name="emoji_list")

EMOJIS = [
    "⚙️",
    "🔧",
    "🛠️",
    "🔒",
    "🗝️",
    "📣",
    "📩",
    "📍",
    "🧪",
    "🧬",
    "🌐",
    "🌍",
    "📌",
    "🎉",
    "🎊",
    "🎁",
    "🎈",
    "🎵",
    "🎤",
]


class EmojiCallback(CallbackData, prefix="emoji_callback"):
    emoji: str


@rt.on_pagination(router, "emoji_list")
async def on_pagination(
    query: CallbackQuery,
    paginator: InlinePaginator,
    state: FSMContext,
    offset: int,
    limit: int,
) -> None:
    data = await state.get_data()
    numbers: list[int] = data.get("numbers", [])

    buttons = []
    for number in numbers[offset : offset + limit]:
        emoji = EMOJIS[number % len(EMOJIS)]
        buttons.append(
            InlineKeyboardButton(
                text=emoji,
                callback_data=EmojiCallback(emoji=emoji).pack(),
            )
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="[–] Remove", callback_data="remove")
    builder.button(text="[+] Add", callback_data="add")

    navigation = paginator.build_navigation()
    builder.attach(builder.from_markup(navigation))

    await paginator.answer("Emoji list:", buttons=buttons, reply_markup=builder.as_markup())


@router.callback_query(EmojiCallback.filter())
async def send_emoji(query: CallbackQuery, callback_data: EmojiCallback):
    await query.answer(text=callback_data.emoji, show_alert=True)
